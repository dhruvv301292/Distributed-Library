import requests as req
from flask import Flask, request
import argparse
from collections import deque
import threading
import logging
import sys
import os
import subprocess
from subprocess import Popen
from applescript import tell
from time import sleep
import pdb

members = deque()
currentPrimary = None
ip_dict = {"S1": 'http://127.0.0.1:5000/', "S2": 'http://127.0.0.1:5010/', "S3": 'http://127.0.0.1:5020/'}
path_dict = {"S1": "PycharmProjects/Distributed/app_passive.py", "S2": "Desktop/18749/app_passive.py", "S3": "Desktop/app_passive.py"}
autorevive = 1

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.disabled = True
app.logger.disabled = True

@app.route("/update")
def update():
    global autorevive
    serverID = request.args.get('id')
    update = request.args.get('up')
    if update == 'add':
        memberlist = addmember(serverID)
    else:
        memberlist = delmember(serverID)
        print("Reviving {}".format(serverID))
        if autorevive == 1:
            print("autorevive: {}".format(autorevive))
            revive(serverID)
    print("RM: {} members: {}".format(len(memberlist), memberlist))
    return "Updated"

def revive(serverID):
    global path_dict
    tell.app('Terminal', 'do script "' + 'python ' + path_dict[serverID] + '"')

def addmember(serverID):
    members.append(serverID)
    # if len(members) == 1:
    #     makePrimary()
    print("Added {}".format(serverID))
    return list(members)

def delmember(serverID):
    members.remove(serverID)
    if len(members) != 0:
        makePrimary()
    print ("Removed {}".format(serverID))
    return list(members)

def makePrimary():
    global ip_dict, currentPrimary
    primary = members[0]
    if primary != currentPrimary:
        ip = ip_dict[primary]
        res = req.get(ip + "setPrim")
        if res.text == "True":
            print("{} is now primary".format(primary))
            currentPrimary = primary

def initmakePrimary(prim):
    global ip_dict, currentPrimary
    primary = prim
    if primary != currentPrimary:
        ip = ip_dict[primary]
        res = req.get(ip + "setPrim")
        if res.text == "True":
            print("{} is now primary".format(primary))
            currentPrimary = primary

def setautorevive(autorev):
    global autorevive
    autorevive = autorev
    print("autorevive set to: {}".format(autorevive))

def startRM(port):
    app.run(debug=False, host="127.0.0.1", port=port)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5008)
    parser.add_argument('--freq', type=float, default=1.0)
    parser.add_argument('--primary', type=str, default="S1")
    parser.add_argument('--auto', type=bool, default = True)
    parser.add_argument('--revive', type=int, default=1)
    args = parser.parse_args ()
    cli = sys.modules['flask.cli']
    cli.show_server_banner = lambda *x: None
    print ( "RM: {} members".format ( len ( members ) ) )
    x = threading.Thread(target=startRM, args=(args.port,))
    x.start()
    tell.app ('Terminal', 'do script "' + 'python PycharmProjects/Distributed/gfd.py' + '"')
    sleep ( 3.0 )
    tell.app ('Terminal', 'do script "' + 'python PycharmProjects/Distributed/lfd2.py --id lfd1' + '"')
    # sleep ( 5.0 )
    tell.app ( 'Terminal', 'do script "' + 'python /Users/dhruvvashisht/Desktop/18749/lfd2.py  --id lfd2' + '"' )
    # sleep ( 5.0 )
    tell.app ( 'Terminal', 'do script "' + 'python /Users/dhruvvashisht/Desktop/lfd2.py  --id lfd3' + '"' )
    sleep ( 5.0 )
    tell.app ('Terminal', 'do script "' + 'python /Users/dhruvvashisht/PycharmProjects/Distributed/app_passive.py' + '"')
    sleep ( 3.0 )
    tell.app ('Terminal', 'do script "' + 'python /Users/dhruvvashisht/Desktop/18749/app_passive.py' + '"')
    sleep ( 3.0 )
    tell.app ( 'Terminal', 'do script "' + 'python /Users/dhruvvashisht/Desktop/app_passive.py' + '"' )
    sleep ( 5.0 )
    # pdb.set_trace()
    setautorevive(args.revive)
    print("revive: {}".format(args.revive))
    initmakePrimary(args.primary)
    sleep(3.0)
    if args.auto:
        tell.app ( 'Terminal', 'do script "' + 'python PycharmProjects/Distributed/tclient.py' + ' --auto True' + '"' )
        with open ( '/Users/dhruvvashisht/PycharmProjects/Distributed/highwater1.txt', 'w' ) as f:
            f.write ( str ( 0 ) )
        tell.app ( 'Terminal', 'do script "' + 'python /Users/dhruvvashisht/Desktop/18749/tclient.py' + ' --auto True' + '"' )
        with open ( '/Users/dhruvvashisht/PycharmProjects/Distributed/highwater2.txt', 'w' ) as f:
            f.write ( str ( 0 ) )
        tell.app ( 'Terminal', 'do script "' + 'python /Users/dhruvvashisht/Desktop/tclient.py' + ' --auto True' + '"' )
        with open ( '/Users/dhruvvashisht/PycharmProjects/Distributed/highwater3.txt', 'w' ) as f:
            f.write ( str ( 0 ) )
