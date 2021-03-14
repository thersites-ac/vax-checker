import requests
import boto3
import time
import os


### entrypoints

def main():
    version = os.environ['VERSION']
    print('query_vax beginning...')
    choice = os.environ['VACCINE_PROVIDER']
    if choice == 'CVS':
        cvs(version)
    elif choice == 'RiteAid':
        riteaid(version)

def cvs(version):
    sns = boto3.resource('sns')
    topic = sns.create_topic(Name = 'CvsVax-{}'.format(version))
    for phone in phones():
        topic.subscribe(Protocol = 'sms', Endpoint = phone)
    for email in emails():
        topic.subscribe(Protocol = 'email', Endpoint = email)
    while True:
        print('Checking CVS...')
        check_cvs(topic)
        time.sleep(30)

def riteaid(version):
    zipcode = os.environ['ZIPCODE']
    sns = boto3.resource('sns')
    topic = sns.create_topic(Name = 'RiteAidVax-{}'.format(version))
    for phone in phones():
        topic.subscribe(Protocol = 'sms', Endpoint = phone)
    for email in emails():
        topic.subscribe(Protocol = 'email', Endpoint = email)
    while True:
        print('Checking RiteAid...')
        check_riteaid(topic, zipcode)
        time.sleep(30)


### vaccine check functions

# cvs requires a referer header, otherwise we get 403'd
def check_cvs(topic):
    headers = { 'referer': 'https://www.cvs.com/immunizations/covid-19-vaccine' }
    resp = requests.get('https://www.cvs.com/immunizations/covid-19-vaccine.vaccine-status.PA.json?vaccineinfo', headers = headers)
    if resp.status_code == 200:
        for entry in resp.json()['responsePayloadData']['data']['PA']:
            if not entry['status'] == 'Fully Booked':
                city = entry['city']
                print('Notifying about', city)
                notify_cvs(topic, city)

# riteaid is straightforward
def check_riteaid(topic, zipcode):
    resp = requests.get('https://www.riteaid.com/services/ext/v2/stores/getStores?address={}&radius=100'.format(zipcode))
    stores = resp.json()['Data']['stores']
    for store in stores:
        url = 'https://www.riteaid.com/services/ext/v2/vaccine/checkSlots?storeNumber={}'.format(store['storeNumber'])
        resp = requests.get(url)
        if resp.status_code == 200 and resp.json()['Data']['slots']['1'] == True:
            addr = store['address']
            print('Notifying about', addr)
            notify_riteaid(topic, '{} in {}, {}'.format(addr, store['city'], store['zipcode']))



### utilities

def notify_cvs(topic, location):
    topic.publish(Message = 'CVS appointment available in {}: https://www.cvs.com/immunizations/covid-19-vaccine'.format(location))


def notify_riteaid(topic, store):
    topic.publish(Message = 'RiteAid appointment available in {}: https://www.riteaid.com/pharmacy/apt-scheduler'.format(store))

def phones():
    return os.environ['PHONE_NUMBERS'].split(',')

def emails():
    return os.environ['EMAILS'].split(',')

# acme in progress... it's more complex




### go

main()
