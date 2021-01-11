import requests as req
from flask import Flask, request
import argparse
import time
import json
from concurrent.futures import ThreadPoolExecutor
import threading
import logging

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.disabled = True
app.logger.disabled = True

messagestack = set()

id = "C1"
ip_dict = {"S1": 'http://127.0.0.1:5000/', "S2": 'http://127.0.0.1:5010/', "S3": 'http://127.0.0.1:5020/'}
req_count = 1
checker = 0

@app.route("/changeprim")
def primUpdate():
    global id, checker
    serverid = request.args.get('server')
    reqCount = request.args.get('reqCount')
    response = request.args.get('response')
    if int(reqCount) in messagestack:
        print("[{}] | request_num {}: Discarded duplicate reply from {}".format(time.strftime("%H:%M:%S", time.localtime()), reqCount, serverid))
    else:
        # serverid, req_count, res.text
        if response != "bleh":
            print ( "[{}] | Received <{}, {}, {}, Response: {}>".format(time.strftime("%H:%M:%S", time.localtime()), serverid, id, reqCount, response))
            messagestack.add(reqCount)
            checker += 1

def connect(ip):
    try:
        print (req.get(ip).text)
    except:
        print("Server is not available")

def trequestinfo(args):
    ip = args[0]
    id = args[1]
    serverid = args[2]
    bookname = args[3]
    req_count = args[4]
    print ( "[{}] | Sending <{}, {}, {}, info {}>".format ( time.strftime ( "%H:%M:%S", time.localtime () ), serverid, id, req_count, bookname ) )
    try:
        requestString = ip + "info?clientId=" + id + "&bookName=" + bookname + "&reqCount=" + str (
            req_count )
        res = req.get ( requestString )
        return serverid, req_count, res.text
    except:
        return serverid, req_count, "Server not available"

def tgetbook(args):
    ip = args[0]
    id = args[1]
    serverid = args[2]
    bookname = args[3]
    req_count = args[4]
    print ( "[{}] | Sending <{}, {}, {}, info {}>".format ( time.strftime ( "%H:%M:%S", time.localtime () ), serverid, id, req_count, bookname ) )
    try:
        requestString = ip + "get?clientId=" + id + "&bookName=" + bookname + "&reqCount=" + str(req_count)
        res = req.get(requestString)
        return serverid, req_count, res.text
    except:
        return serverid, req_count, "Server not available"


def requestinfo(bookname):
    global messagestack, ip_dict, id, req_count
    with open ( '/Users/dhruvvashisht/PycharmProjects/Distributed/members.txt', 'r' ) as f:
        members = json.load ( f )

    if len(members) == 0:
        print("No servers online")
        return

    urls = []
    for member in members:
        inputarg = (ip_dict[member], id, member, bookname, req_count)
        urls.append(inputarg)

    with ThreadPoolExecutor ( max_workers=3 ) as pool:
        responses = list(pool.map(trequestinfo, urls))

    for response in responses:
        if response[2] == "Server not available":
            continue
        elif response[1] in messagestack:
            # print ( "request_num {}: Discarded duplicate reply from {}".format ( response[1], response[0] ) )
            pass
        else:
            print ( "[{}] | Received <{}, {}, {}, Response: {}>".format (
                time.strftime ( "%H:%M:%S", time.localtime () ), response[0], id, response[1], response[2] ) )
            messagestack.add ( response[1] )
    req_count += 1

def getbook(bookname):
    global messagestack, ip_dict, id, req_count, checker, watermark_dict
    with open ( '/Users/dhruvvashisht/PycharmProjects/Distributed/members.txt', 'r' ) as f:
        members = json.load ( f )

    if len(members) == 0:
        print("No servers online")
        return

    urls = []
    for member in members:
        inputarg = (ip_dict[member], id, member, bookname, req_count)
        urls.append(inputarg)

    with ThreadPoolExecutor ( max_workers=3 ) as pool:
        responses = list(pool.map(tgetbook, urls))

    for response in responses:
        serverid = response[0]
        reqCount = response[1]
        res_string = response[2]
        if res_string == "Server not available":
            continue
        elif reqCount in messagestack:
            # print ( "request_num {}: Discarded duplicate reply from {}".format ( response[1], response[0] ) )
            pass
        else:
            if res_string != "bleh":
                print ( "[{}] | Received <{}, {}, {}, Response: {}>".format (time.strftime ( "%H:%M:%S", time.localtime () ), response[0], id, response[1], response[2] ) )
                messagestack.add ( reqCount )
                with open('/Users/dhruvvashisht/PycharmProjects/Distributed/highwater1.txt', 'w') as f:
                    f.write(str(reqCount))
                checker += 1
    req_count += 1

def set_dict(ipdict):
    global ip_dict
    ip_dict = ipdict

def startClient(port):
    app.run(debug=False, host="127.0.0.1", port=port)

def getCount():
    global checker
    return checker

def setreqcount():
    global req_count
    with open ( '/Users/dhruvvashisht/PycharmProjects/Distributed/highwater1.txt', 'r' ) as f1:
        req_count = int ( f1.readline () ) + 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser ()
    parser.add_argument('--id', type=str, default='C1')
    parser.add_argument('--ip1', type=str, default='http://127.0.0.1:5000/')
    parser.add_argument ('--ip2', type=str, default='http://127.0.0.1:5010/')
    parser.add_argument ('--ip3', type=str, default='http://127.0.0.1:5020/')
    parser.add_argument('--auto', type=bool, default=False)
    args = parser.parse_args()


    com1 = args.ip1
    com2 = args.ip2
    com3 = args.ip3
    setreqcount()
    ip_dictionary = {"S1": com1, "S2": com2, "S3": com3}
    set_dict(ip_dictionary)
    x = threading.Thread(target=startClient, args=((5070,)))
    x.start()


    connect(com1)
    if not args.auto:
        print("Enter request type and book name")
        while True:
            inp = input()
            if (inp == 'q'):
                break
            else:
                reqlist = inp.split ( ' ', 1)
                if len(reqlist) < 2:
                    print('Incorrect format. Enter request type and book name')
                    continue
                if reqlist[0] == 'i' or reqlist[0] == 'info':
                    requestinfo(reqlist[1])
                elif reqlist[0] == 'req' or reqlist[0] == 'request':
                    getbook(reqlist[1])

    else:
        count = 0
        start = time.time ()
        while True:
            getbook ("Asterix")
            count += 1
            # if count == 300:
            #     break
            time.sleep(0.5 - ((time.time () - start) % 0.5))
        time.sleep(2)
        print("requests sent: {}".format(count))
        print("books received: {}".format(getCount()))
