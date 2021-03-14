import requests
import boto3
import time
import env
import logging

logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)


### entrypoints

def main():
    logging.info('query_vax beginning...')
    if env.provider == 'CVS':
        cvs(env.version)
    elif env.provider == 'RiteAid':
        riteaid(env.version)

def cvs(version):
    sns = boto3.resource('sns')
    topic = sns.create_topic(Name = 'CvsVax-{}'.format(version))
    cvs_avail = set()
    for email in emails():
        topic.subscribe(Protocol = 'email', Endpoint = email)
    while True:
        logging.info('Checking CVS...')
        cvs_avail = check_cvs(topic, cvs_avail)
        time.sleep(30)

def riteaid(version):
    sns = boto3.resource('sns')
    topic = sns.create_topic(Name = 'RiteAidVax-{}'.format(version))
    riteaid_avail = set()
    for email in emails():
        topic.subscribe(Protocol = 'email', Endpoint = email)
    while True:
        logging.info('Checking RiteAid...')
        riteaid_avail = check_riteaid(topic, env.zipcode, riteaid_avail)
        time.sleep(30)


### vaccine check functions

def check_cvs(topic, cvs_avail):
    headers = { 'referer': 'https://www.cvs.com/immunizations/covid-19-vaccine' }
    resp = requests.get('https://www.cvs.com/immunizations/covid-19-vaccine.vaccine-status.PA.json?vaccineinfo', headers = headers)
    if resp.status_code == 200:
        entries = [ entry for entry in resp.json()['responsePayloadData']['data']['PA'] if not entry['status'] == 'Fully Booked' and entry['city'] not in cvs_avail ]
        for entry in entries:
            notify_cvs(topic, entry['city'])
        return { entry['city'] for entry in entries }
    else:
        logging.error('CVS query failed with status code {}'.format(resp.status_code))
        return cvs_avail

def check_riteaid(topic, zipcode, riteaid_avail):
    resp = requests.get('https://www.riteaid.com/services/ext/v2/stores/getStores?address={}&radius=100'.format(zipcode))
    if resp.status_code == 200:
        entries = [ entry for entry in resp.json()['Data']['stores'] if entry['storeNumber'] not in riteaid_avail ]
        for entry in entries:
            storeNumber = entry['storeNumber']
            url = 'https://www.riteaid.com/services/ext/v2/vaccine/checkSlots?storeNumber={}'.format(storeNumber)
            store_resp = requests.get(url)
            if store_resp.status_code == 200 and store_resp.json()['Data']['slots']['1'] == True:
                notify_riteaid(topic, '{} in {}, {}'.format(entry['address'], entry['city'], entry['zipcode']))
            elif not store_resp.status_code == 200:
                logging.error('RiteAid checkSlots query for store {} failed with status code {}'.format(storeNumber, store_resp.status_code))
        return { entry['storeNumber'] for entry in entries }
    else:
        logging.error('RiteAid getStores query failed with status code {}'.format(resp.status_code))
        return riteaid_avail



### utilities

def notify_cvs(topic, location):
    logging.info('Notifying about'.format(location))
    topic.publish(Message = 'CVS appointment available in {}: https://www.cvs.com/immunizations/covid-19-vaccine'.format(location))


def notify_riteaid(topic, store):
    logging.info('Notifying about {}'.format(store))
    topic.publish(Message = 'RiteAid appointment available in {}: https://www.riteaid.com/pharmacy/apt-scheduler'.format(store))

def emails():
    return env.emails.split(',')

# acme in progress... it's more complex




### go

main()
