from flask import Flask, request
import time
import logging
import argparse
import json
from concurrent.futures import ThreadPoolExecutor
import requests as req
from collections import deque
import pdb

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.disabled = True
app.logger.disabled = True

library = {}
library["Asterix"] = 10000
library["Harry Potter"] = 7000
library["Dune"] = 3000

serverid = "S1"
ip_dict = {"S1": 'http://127.0.0.1:5000/', "S2": 'http://127.0.0.1:5010/', "S3": 'http://127.0.0.1:5020/'}
client_dict = {"C1": 'http://127.0.0.1:5070/', "C2": 'http://127.0.0.1:5080/', "C3": 'http://127.0.0.1:5090/'}
watermark_dict = {"C1": 0, "C2": 0, "C3": 0}
messagecount = 0
ckptcount = 0
ckptfreq = 2
isPrimary = False

messagelist = deque()

@app.route("/checkpoint", methods=['POST'])
def recieveckpt():
    global library, ckptcount, messagelist, messagecount
    templist = messagelist
    messagelist.clear()
    data = request.get_json()
    primary = data["prim"]
    print("state before checkpoint: {}".format(library))
    print("message list before checkpoint: {}".format(templist))
    library = data["state"]
    ckptcount = data["ckptcount"]
    print("[{}] Received checkpoint from {} | Checkpoint count: {}".format(time.strftime("%H:%M:%S", time.localtime()), primary, ckptcount))
    print("state after checkpoint: {}".format(library))
    messagecount = 0
    print ( "message list after checkpoint: {}".format(messagelist))
    return "True"


@app.route("/")
def intro():
    introString = "Welcome to the library. You may borrow the following books:\n"
    for key in library:
        introString += str(key) + "\n"
    return introString

@app.route("/heartbeat")
def heartbeat():
    lfdid = request.args.get('id')
    beatcount = request.args.get('count')
    print("[{}] Heartbeat received from {} | beat count: {}".format(time.strftime("%H:%M:%S", time.localtime()), lfdid, beatcount))
    print("[{}] Sending response to {} | beat count: {}".format(time.strftime("%H:%M:%S", time.localtime()), lfdid, beatcount))
    print(str(library))
    return "Alive"

@app.route("/info")
def infoBook():
    global serverid, messagecount, ckptfreq, isPrimary
    clientid = request.args.get('clientId')
    bookName = request.args.get('bookName')
    reqCount = request.args.get('reqCount')
    print ("[{}] | Received <{}, {}, {}, Request: info {}>".format ( time.strftime ( "%H:%M:%S", time.localtime () ), clientid, serverid, reqCount, bookName))
    messagelist.append((clientid, reqCount, "info", bookName))
    if isPrimary:
        print ("State before processing <{}, {}, {}, Request: info {}>:".format(clientid, serverid, reqCount, bookName) + str(library))
        if bookName in library.keys() and library.get(bookName) != 0:
            infoString = "Yes! {} copy/copies of {} available!".format(library.get(bookName), bookName)
            print ("State after processing <{}, {}, {}, Request: info {}>:".format(clientid, serverid, reqCount, bookName) + str(library))
            print ("[{}] | Sending <{}, {}, {}, Response: {}>".format ( time.strftime ( "%H:%M:%S", time.localtime () ),clientid, serverid, reqCount, infoString))

        else:
            infoString = "Sorry! {} is not available at the moment.".format(bookName)
            print ( "State after processing <{}, {}, {}, Request: info {}>:".format(clientid, serverid, reqCount, bookName) + str(library))
            print ( "[{}] | Sending <{}, {}, {}, Response: {}>".format(time.strftime("%H:%M:%S", time.localtime () ), clientid, serverid, reqCount, infoString))
    else:
        infoString = "Message ID saved"
    messagecount += 1
    print (messagecount)
    if messagecount == ckptfreq and isPrimary:
        sendcheckpoint()
        messagecount = 0
    return infoString

@app.route("/setPrim")
def primRequest():
    global serverid, messagelist, client_dict, library, watermark_dict
    print("SOMETHING DIED!!!")
    if len(messagelist) != 0:
        ### MAKE CHANGES HERE ###
        print("I do not have the latest state. Let me quesce.")
        with open ( '/Users/dhruvvashisht/PycharmProjects/Distributed/highwater1.txt', 'r' ) as f1:
            watermark_dict["C1"] = int(f1.readline())
        with open ( '/Users/dhruvvashisht/PycharmProjects/Distributed/highwater2.txt', 'r' ) as f2:
            watermark_dict["C2"] = int(f2.readline())
        with open ( '/Users/dhruvvashisht/PycharmProjects/Distributed/highwater3.txt', 'r' ) as f3:
            watermark_dict["C3"] = int(f3.readline())
        print("high watermark: {}".format(watermark_dict))
        print("pending messages: {}".format(messagelist))
        while len(messagelist) != 0:
            clientid, reqCount, reqType, bookName = messagelist.popleft()
            # print("reqCount = {}".format(type(reqCount)))
            # print ("watermark = {}".format ( type ( watermark_dict[clientid] ) ) )
            if reqCount <= watermark_dict[clientid]:
                print("[{}] | Client: {}| Request: {} | Updating state but not responding".format(time.strftime("%H:%M:%S", time.localtime()), clientid, reqCount))
                if bookName in library.keys () and library.get ( bookName ) != 0:
                    library[bookName] = library.get ( bookName ) - 1
            elif reqType == "get":
                print ( "State before processing <{}, {}, {}, Request: get {}>:".format ( clientid, serverid, reqCount, bookName ) + str (library))
                if bookName in library.keys () and library.get ( bookName ) != 0:
                    library[bookName] = library.get ( bookName ) - 1
                    getString = "Yes! {} has been shared with you! {} more copy/copies available!".format ( bookName, library.get (bookName ) )
                    print("State after processing <{}, {}, {}, Request: info {}>:".format(clientid, serverid, reqCount, bookName) + str(library))
                    print("[{}] | Sending <{}, {}, {}, Response: {}>".format(time.strftime("%H:%M:%S", time.localtime()), clientid, serverid, reqCount, getString))
                else:
                    getString = "Sorry! {} is not available at the moment.".format ( bookName )
                    print ( "State after processing <{}, {}, {}, Request: info {}>:".format ( clientid, serverid,
                                                                                              reqCount,
                                                                                              bookName ) + str (library ) )
                    print ( "[{}] | Sending <{}, {}, {}, Response: {}>".format (
                        time.strftime ( "%H:%M:%S", time.localtime () ), clientid, serverid, reqCount, getString ) )
                try:
                    responseString = client_dict[clientid] + "changeprim?server=" + serverid + "&reqCount=" + str (reqCount) + "&response=" + getString
                    req.get(responseString)
                    # watermark_dict[clientid] = reqCount
                    # with open('/Users/dhruvvashisht/PycharmProjects/Distributed/highwater.txt', 'w') as f:
                    #     json.dump ( watermark_dict, f )
                    # print("watermark_dict updated: {}".format(watermark_dict))
                except:
                    print("Client is not up.")
        print("message list cleared")
    if set_Primary():
        print("{} is now primary!".format(serverid))
    return "True"

@app.route("/get")
def getBook():
    global isPrimary, serverid, messagecount, ckptfreq, watermark_dict
    clientid = request.args.get('clientId')
    bookName = request.args.get('bookName')
    reqCount = int(request.args.get('reqCount'))
    # print(type(reqCount))
    print ( "[{}] | Received <{}, {}, {}, Request: get {}>".format ( time.strftime ( "%H:%M:%S", time.localtime () ), clientid, serverid, reqCount, bookName ) )
    messagelist.append((clientid, reqCount, "get", bookName))
    if isPrimary:
        print ( "State before processing <{}, {}, {}, Request: get {}>:".format ( clientid, serverid, reqCount, bookName ) + str (library ) )
        if bookName in library.keys() and library.get(bookName) != 0:
            library[bookName] = library.get(bookName) - 1
            getString = "Yes! {} has been shared with you! {} more copy/copies available!".format(bookName, library.get(bookName))
            print("State after processing <{}, {}, {}, Request: info {}>:".format ( clientid, serverid, reqCount, bookName ) + str(library))
            print("[{}] | Sending <{}, {}, {}, Response: {}>".format ( time.strftime ( "%H:%M:%S", time.localtime () ), clientid, serverid, reqCount, getString))

        else:
            getString = "Sorry! {} is not available at the moment.".format ( bookName )
            print ( "State after processing <{}, {}, {}, Request: info {}>:".format ( clientid, serverid, reqCount, bookName ) + str(library))
            print ( "[{}] | Sending <{}, {}, {}, Response: {}>".format ( time.strftime ( "%H:%M:%S", time.localtime () ), clientid, serverid, reqCount, getString ) )
        # watermark_dict[clientid] = reqCount
        # with open('/Users/dhruvvashisht/PycharmProjects/Distributed/highwater.txt', 'w') as f:
        #     json.dump(watermark_dict, f)
        # print("[{}] | High watermark updated as primary: {}".format(time.strftime ( "%H:%M:%S", time.localtime () ), watermark_dict))

    else:
        getString = "bleh"
        print ("[{}] | Message Id {} saved>".format ( time.strftime ( "%H:%M:%S", time.localtime () ), reqCount))
    messagecount += 1
    print(messagecount)
    # pdb.set_trace()
    if messagecount != 0 and messagecount % ckptfreq == 0 and isPrimary:
        sendcheckpoint()
        messagecount = 0
    return getString

def sendcheckpoint():
    # pdb.set_trace()
    global serverid, ip_dict, ckptcount
    ckptcount += 1
    with open('/Users/dhruvvashisht/PycharmProjects/Distributed/members.txt', 'r') as f:
        members = json.load(f)
    urls = []
    backupString = ""
    membercount = 0
    for member in members:
        membercount += 1
        if member != serverid:
            inputarg = (ip_dict[member], ckptcount)
            urls.append(inputarg)
            backupString += member
            if membercount < len(members):
                backupString += ", "

    print("[{}] | Sending checkpoint to {} | Checkpoint count: {}".format(time.strftime("%H:%M:%S", time.localtime()), backupString, ckptcount))

    if len(urls) != 0:
        with ThreadPoolExecutor(max_workers=len(urls)) as pool:
            pool.map(checkpoint, urls)

def checkpoint(args):
    global library
    url = args[0]
    count = args[1]
    data = {"prim": serverid, "state": library, "ckptcount": count}
    try:
        response = req.post(url + "checkpoint", json=data)
        if response.text == "True":
            print("Checkpoint Success")
    except:
        print("Checkpoint failed")
        return

def set_ckpt_freq(cf):
    global ckptfreq
    ckptfreq = cf

def set_Primary():
    global isPrimary
    isPrimary = True
    return isPrimary

def set_ID(id):
    global serverid
    serverid = id


if __name__ == "__main__":
    parser = argparse.ArgumentParser ()
    parser.add_argument ('--id', type=str, default='S1')
    parser.add_argument ( '--isPrimary', type=bool, default=False)
    parser.add_argument('--ckfreq', type=int, default=10)
    args = parser.parse_args()

    if args.isPrimary:
        prim = set_Primary()

    if args.id != "S1":
        set_ID(args.id)

    set_ckpt_freq(args.ckfreq)

    app.run(debug=True, host="127.0.0.1", port=5000)
