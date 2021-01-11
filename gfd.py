import requests as req
import time
import argparse
from collections import deque
import threading
import json
import pdb


members = deque()

def heartbeat(ip, freq, serverID):
        start = time.time()
        connected = False
        while True:
            try:
                resp = req.get(ip + "gfdbeat")
                if resp.text == "Alive" and not connected:
                    res = req.get("http://127.0.0.1:5008/update?id={}&up=add".format(serverID))
                    memberlist = addmember ( serverID )
                    print("GFD: {} members: {}".format(len(memberlist), memberlist))
                    # pdb.set_trace()
                    with open('/Users/dhruvvashisht/PycharmProjects/Distributed/members.txt', 'w') as f:
                        json.dump(memberlist, f)
                        print("printed to members")
                    connected = True
                elif resp.text == "Dead" and connected:
                    res = req.get("http://127.0.0.1:5008/update?id={}&up=remove".format(serverID))
                    memberlist = delmember ( serverID )
                    if len(memberlist) == 0:
                        print("GFD: {} members".format(len(memberlist)))
                    else:
                        print("GFD: {} members: {}".format(len(memberlist), memberlist))
                    connected = False
                    with open ( '/Users/dhruvvashisht/PycharmProjects/Distributed/members.txt', 'w' ) as f:
                        json.dump (memberlist, f)
                time.sleep(freq - ((time.time() - start) % freq))
            except:
                if connected:
                    memberlist = delmember(serverID)
                    if len ( memberlist ) == 0:
                        print ( "GFD: {} members".format ( len ( memberlist ) ) )
                    else:
                        print ( "GFD: {} members: {}".format ( len ( memberlist ), memberlist ) )
                    connected = False
                time.sleep(freq - ((time.time () - start) % freq))

def addmember(serverID):
    members.append(serverID)
    print("Added {}".format(serverID))
    return list(members)

def delmember(serverID):
    members.remove(serverID)
    print("Removed {}".format(serverID))
    return list(members)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip1', type=str, default='http://127.0.0.1:5002/')
    parser.add_argument('--ip2', type=str, default='http://127.0.0.1:5004/')
    parser.add_argument('--ip3', type=str, default='http://127.0.0.1:5006/')
    parser.add_argument('--freq', type=float, default=1.0)
    args = parser.parse_args ()
    print("GFD: {} members".format(len(members)))
    x1 = threading.Thread ( target=heartbeat, args=(args.ip1, args.freq, "S1"))
    x1.start()
    x2 = threading.Thread ( target=heartbeat, args=(args.ip2, args.freq, "S2"))
    x2.start()
    x3 = threading.Thread ( target=heartbeat, args=(args.ip3, args.freq, "S3"))
    x3.start()