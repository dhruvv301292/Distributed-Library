from flask import Flask, request
import time
import argparse
from collections import deque
import requests as req
app = Flask(__name__)

library = {}
library["Asterix"] = 5
library["Harry Potter"] = 7
library["Dune"] = 3
resurrected = -1
serverid = 1

secondary = { "S1": 'http://127.0.0.1:5000/',"S2": 'http://127.0.0.1:5001/', "S3": 'http://127.0.0.1:5002/'}
checkpt_count = 0
messagelist = deque()
messagecount = 0
checkpt_freq = 2
isReady = True 

@app.route("/")
def intro():
    introString = "Welcome to the library. You may borrow the following books:\n"
    for key in library:
        introString += str(key) + "\n"
    return introString

@app.route("/heartbeat/<lfdid>")
def heartbeat(lfdid):
    print("[{}] Heartbeat received from {}".format(time.strftime("%H:%M:%S", time.localtime()), lfdid))
    print ( "[{}] Sending response to {}".format ( time.strftime ( "%H:%M:%S", time.localtime () ), lfdid ) )
    print()
    return "Alive"

@app.route("/info")
def infoBook():
    global messagelist, checkpt_freq, messagecount, resurrected 
    
    clientid = request.args.get('clientId')
    bookName = request.args.get('bookName')
    reqCount = request.args.get('reqCount')
    print ("[{}] | Received <{}, {}, {}, Request: info {}>".format ( time.strftime ( "%H:%M:%S", time.localtime () ), clientid, args.id, reqCount, bookName))
    print ("State before processing <{}, {}, {}, Request: info {}>:".format(clientid, args.id, reqCount, bookName) + str(library))
    messagelist.append(reqCount)
    if bookName in library.keys() and library.get(bookName) != 0:
        infoString = "Yes! {} copy/copies of {} available!".format(library.get(bookName), bookName)
        print ("State after processing <{}, {}, {}, Request: info {}>:".format(clientid, args.id, reqCount, bookName) + str(library))
        print ("[{}] | Sending <{}, {}, {}, Response: {}>".format ( time.strftime ( "%H:%M:%S", time.localtime () ),clientid, args.id, reqCount, infoString))
        
        # return infoString

    else:
        infoString = "Sorry! {} is not available at the moment.".format(bookName)
        print ( "State after processing <{}, {}, {}, Request: info {}>:".format(clientid, args.id, reqCount, bookName) + str(library))
        print ( "[{}] | Sending <{}, {}, {}, Response: {}>".format(time.strftime("%H:%M:%S", time.localtime () ), clientid, args.id, reqCount, infoString))
        # return infoString
    
    messagecount += 1
    print("Message count:" , messagecount)

    #will remove this chept freq part. Yeah I know freq isnt for active but for passive isntead. I just wanted to make this part run first. 
    if messagecount == checkpt_freq:
        sendCheckpoint()
        messagecount = 0
        isReady = True

    return infoString



@app.route("/get/")
def getBook():
    global messagecount, checkpt_freq, resurrected
    clientid = request.args.get('clientId')
    bookName = request.args.get('bookName')
    reqCount = request.args.get('reqCount')
    print ( "[{}] | Received <{}, {}, {}, Request: get {}>".format ( time.strftime ( "%H:%M:%S", time.localtime () ), clientid, args.id, reqCount, bookName ) )
    print ( "State before processing <{},{}, {}, Request: get {}>:".format ( clientid, args.id, reqCount, bookName ) + str (library ) )
    messagelist.append(reqCount)
    if isReady == True:
        if bookName in library.keys() and library.get(bookName) != 0:
            library[bookName] = library.get(bookName) - 1
            getString = "Yes! {} has been shared with you! {} more copy/copies available!".format(bookName, library.get(bookName))
            print("State after processing <{}, {}, {}, Request: info {}>:".format ( clientid, args.id, reqCount, bookName ) + str(library))
            print("[{}] | Sending <{}, {}, {}, Response: {}>".format ( time.strftime ( "%H:%M:%S", time.localtime () ), clientid, args.id, reqCount, getString))

        else:
            getString = "Sorry! {} is not available at the moment.".format ( bookName )
            print ( "State after processing <{}, {}, {}, Request: info {}>:".format ( clientid, args.id, reqCount, bookName ) + str(library))
            print ( "[{}] | Sending <{}, {}, {}, Response: {}>".format ( time.strftime ( "%H:%M:%S", time.localtime () ), clientid, args.id, reqCount, getString ) )
    
    messagecount += 1
    print("Message count:" , messagecount)
    
    if messagecount != 0 and messagecount % checkpt_freq == 0:
        sendCheckpoint()
        messagecount = 0
        isReady == True

    return getString
    

        
def sendCheckpoint():
    global secondary,checkpt_count, library
    checkpt_count += 1

    payload = {"state":library, "checkpt_count": checkpt_count}
    try:        
        for replica in secondary.keys():
            payload['sender'] = replica
            reqString = secondary.get(replica) + "checkpoint"
            print(reqString)
            response = req.post(reqString, json=payload)
            if response.text == "True":
                print("Checkpoint successfully sent.")
            else:
                print("Response text:", response.text)
                print("Did something with checkpoint")
    except:
        print("Checkpoint sending failed.")
    return

@app.route('/checkpoint', methods=['POST'])
def receiveCheckpoint():
    global library, checkpt_count, messagelist
    data = request.get_json()

    print("State before checkpoint: {}".format(library))
    print("Message list before checkpoint: {}".format(messagelist))

    library = data['state']
    checkpt_count = data['checkpt_count']
    sending_server = data['sender']

    print("[{}] Received checkpoint from {} | Checkpoint count: {}".format(time.strftime("%H:%M:%S", time.localtime()), sending_server, checkpt_count))
    print("state after checkpoint: {}".format(library))

    messagelist.clear()
    print ( "Message list after checkpoint: {}".format(messagelist))    

    return "True"
    
@app.route("/watchtower")
def watch():
    global resurrected
    resurrected = request.args.get('new') 
    print("Server {} notified that resurr member is:{}".format(args.port, resurrected))
    return "Notified."


if __name__ == "__main__":
    parser = argparse.ArgumentParser ()
    parser.add_argument('--id', type=str, default='S1')
    parser.add_argument('--port', type=int, default=5000)
    # parser.add_argument('--checkpt_freq', type=int, default=2)


    args = parser.parse_args ()
    app.run(debug=True, port=args.port)
