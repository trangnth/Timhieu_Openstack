#!/usr/bin/python

#
# Script send notify aodh via telegram
#


from flask import Flask, request
import requests
import json
import logging
app = Flask(__name__)

TOKEN = "554277548:AAF6SPBbVrE9Q3XNpIuYDdfiIO_EW32wNMg"
#URL = "https://api.telegram.org/bot{}/sendMessage?text={}&chat_id={}".format(TOKEN, notify,chat_id)
CHAT_ID = "518674763"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
loger = logging.getLogger(__name__)

@app.route("/cpu", methods=['POST'])
def alarm_cpu():
    status = json.loads(request.data)['current']
    reason = json.loads(request.data)['reason']
    value = json.loads(request.data)['reason_data']['most_recent']
    previous = json.loads(request.data)['previous']
    notify='''
            *STATUS OF CPU CHANGED*
        STATUS: `{0}`
        REASON: `{1}`
        VALUE: `{2}`
        PREVIOUS STATUS: `{3}`
            '''.format(status, reason, value, previous)
    json_payload = {
        "text" : notify,
        "channel" : "#aodh-alerts",
        "username" : "trangnth",
    }

    headers = {'content-type': 'application/json', 'accept': 'application'}
    requests.post(url='https://api.telegram.org/bot{}/sendMessage?text={}&chat_id={}'.format(TOKEN, notify, CHAT_ID),
                                       data=json.dumps(json_payload),
                                       headers=headers)
    requests.post(url='https://hooks.slack.com/services/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',
                                       data=json.dumps(json_payload),
                                       headers=headers)
    return "cpu was changed"
    
@app.route("/memory", methods=['POST'])
def alarm_memory():
    status = json.loads(request.data)['current']
    reason = json.loads(request.data)['reason']
    value = json.loads(request.data)['reason_data']['most_recent']
    previous = json.loads(request.data)['previous']
    notify='''
            *STATUS OF MEMORY CHANGED*
        STATUS: `{0}`
        REASON: `{1}`
        VALUE: `{2}`
        PREVIOUS STATUS: `{3}`
            '''.format(status, reason, value, previous)
    json_payload = {
        "text" : notify,
        "channel" : "#aodh-alerts",
        "username" : "trangnth",
    }

    headers = {'content-type': 'application/json', 'accept': 'application'}
    requests.post(url='https://hooks.slack.com/services/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',
                                       data=json.dumps(json_payload),
                                       headers=headers)
    return "memory was changed"
    
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5123)