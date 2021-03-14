import requests
import boto3
import time
import os


### entrypoints

def cvs():
    sns = boto3.resource('sns')
    topic = sns.create_topic(Name = 'CVS vaccine notifications')
    for phone in phones():
        topic.subscribe(Protocol = 'sms', Endpoint = phone)
    for email in emails():
        topic.subscribe(Protocol = 'email', Endpoint = email)
    while True:
        check_cvs()
        time.sleep(30)

def riteaid():
    sns = boto3.resource('sns')
    topic = sns.create_topic(Name = 'RiteAid vaccine notifications')
    for phone in phones():
        topic.subscribe(Protocol = 'sms', Endpoint = phone)
    for email in emails():
        topic.subscribe(Protocol = 'email', Endpoint = email)
    while True:
        check_riteaid()
        time.sleep(30)


### vaccine check functions

# cvs requires a referer header, otherwise we get 403'd
def check_cvs():
    headers = { 'referer': 'https://www.cvs.com/immunizations/covid-19-vaccine' }
    resp = requests.get('https://www.cvs.com/immunizations/covid-19-vaccine.vaccine-status.PA.json?vaccineinfo', headers = headers)
    if resp.status_code == 200:
        for entry in resp.json()['responsePayloadData']['data']['PA']:
            if not entry['status'] == 'Fully Booked':
                notify_cvs(entry['city'])

# riteaid is straightforward
def check_riteaid():
    resp = requests.get('https://www.riteaid.com/services/ext/v2/stores/getStores?address=19086&radius=100')
    stores = resp.json()['Data']['stores']
    for store in stores:
        url = 'https://www.riteaid.com/services/ext/v2/vaccine/checkSlots?storeNumber={}'.format(store['storeNumber'])
        resp = requests.get(url)
        if resp.status_code == 200 and resp.json()['Data']['slots']['1'] == True:
            notify_riteaid('{} in {}, {}'.format(store['address'], store['city'], store['zipcode']))



### utilities

def notify_cvs(topic, location):
    topic.publish(Message = 'CVS appointment available in {}'.format(location))


def notify_riteaid(topic, store):
    topic.publish(Message = 'RiteAid appointment available in {}'.format(store))

def phones():
    return os.environ['PHONE_NUMBERS'].split(',')

def emails():
    return os.environ['EMAILS'].split(',')

# acme in progress... it's more complex
