from flask import Flask, Response, request, render_template
from collections import deque
import json
import requests
from requests.auth import HTTPBasicAuth

AUTH_ID = 'MANZMXYWEXOWI1OTE4M2'
AUTH_TOKEN = 'MzdlY2Q5NzczMmM3M2NjODhiOWZmNTg4NTk4N2Nk'

app = Flask(__name__, static_url_path='')

call_queue = deque()

@app.route('/answer_url/', methods=['GET'])
def answer():
    CallUUID = request.args.get('CallUUID')
    if len(call_queue) == 0 or CallUUID in call_queue:
        nxml = """
               <Response>
               <Dial>
               <Number>+919019188898</Number>
               </Dial>
              </Response>
              """
        xml = """
              <Response>
              <Dial>
              <User>sip:testuser150714135336@phone.plivo.com</User>
              </Dial>
              </Response>
              """
        if CallUUID not in call_queue:
            call_queue.append(CallUUID)
    else:
        call_queue.append(CallUUID)
        # Return the xml play response
        xml = """
              <Response>
              <Play loop="0">https://s3.amazonaws.com/plivocloud/Trumpet.mp3</Play>
              </Response>
              """

    print "Response returned is", xml
    return Response(xml, mimetype='text/xml')



@app.route('/hangup_url/', methods=['GET'])
def hangup():
    args = request.args.get('CallUUID')
    CallUUID = call_queue.popleft()
    if len(call_queue) >= 1:
        CallUUID = call_queue[0]
        url = "https://api.plivo.com/v1/Account/%s/Call/%s/" % (AUTH_ID, CallUUID)
        payload = {'aleg_url': 'http://1342cd8a.ngrok.io/answer_url/', 'aleg_method': 'GET'}
        headers = {'content-type': 'application/json'}
        response = requests.post(url, auth=HTTPBasicAuth(AUTH_ID, AUTH_TOKEN), headers=headers, data=json.dumps(payload))
        if response.status_code != 202:
            #log an error 
            print "Some Error Happened"

    return Response('', mimetype='text/xml')


@app.route('/outbound_call_url/', methods=['GET', 'POST'])
def outbound_call():

    xml = """<Response> 
            <Dial callerId="18004321321">
            <Number>18001231</Number> 
            </Dial> 
            </Response>"""
    url = "https://api.plivo.com/v1/Account/%s/Call/" % AUTH_ID
    payload = {'from' : '+18887484765',
               'to' : '+18887484570',
               'answer_url': 'http://1342cd8a.ngrok.io/answer_url/'}
    headers = {'content-type': 'application/json'}
    response = requests.post(url, auth=HTTPBasicAuth(AUTH_ID, AUTH_TOKEN), headers=headers, data=json.dumps(payload))
    print response,response.status_code
    return Response("DONE")


@app.route('/')
def hello(name="Phone"):
    return render_template('phone.html', name=name)




if __name__ == "__main__":
    app.run(debug=True)