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

servers = { "1": 'http://127.0.0.1:5000/',"2": 'http://127.0.0.1:5001/', "3": 'http://127.0.0.1:5002/'}
server_ports = {"1": 5000, "2": 5001, "3": 5002}
checkpt_count = 0
messagelist = deque()
messagecount = 0
checkpt_freq = 2
isReady = {5000: True, 5001: True, 5002: True}

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
    global messagelist, checkpt_freq, messagecount, resurrected, isReady

    # if args.port != server_ports.get(resurrected): #something missing here, isReady condition!!
    if isReady.get(args.port) == True: 
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


    
    else:
        sendCheckpoint()
        messagecount = 0
        isReady = True
        print("Resurrected server S{} is ready now.".format(resurrected))

    return infoString



@app.route("/get/")
def getBook():
    global messagecount, checkpt_freq, resurrected, isReady
    # if args.port != server_ports.get(resurrected): #something missing here, isReady condition!!
    if isReady.get(args.port) == True: 
        clientid = request.args.get('clientId')
        bookName = request.args.get('bookName')
        reqCount = request.args.get('reqCount')
        print ( "[{}] | Received <{}, {}, {}, Request: get {}>".format ( time.strftime ( "%H:%M:%S", time.localtime () ), clientid, args.id, reqCount, bookName ) )
        print ( "State before processing <{},{}, {}, Request: get {}>:".format ( clientid, args.id, reqCount, bookName ) + str (library ) )
        messagelist.append(reqCount)

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
    

        
    else:
        sendCheckpoint()
        messagecount = 0
        isReady = True
        print("Resurrected server {} is ready now.".format(resurrected))

    return getString
    

        
def sendCheckpoint():
    global servers,checkpt_count, library, resurrected
    checkpt_count += 1

    payload = {"state":library, "checkpt_count": checkpt_count}
    try:        
        for replica in servers.keys():
            if replica != resurrected:
                payload['sender'] = replica
                reqString = servers.get(replica) + "checkpoint"
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
    global library, checkpt_count, messagelist, resurrected
    if args.port == server_ports.get(resurrected):
        print("Checkpoint received at server: S", resurrected)
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
    global resurrected, isReady
    resurrected = request.args.get('new') 
    resurr_port = server_ports.get(resurrected)
    isReady[resurr_port] = False
    print("Server port {} notified that resurr member is:{}".format(args.port, resurrected))
    return "Notified."


if __name__ == "__main__":
    parser = argparse.ArgumentParser ()
    parser.add_argument('--id', type=str, default='S1')
    parser.add_argument('--port', type=int, default=5000)
    # parser.add_argument('--checkpt_freq', type=int, default=2)


    args = parser.parse_args ()
    app.run(debug=True, port=args.port)
