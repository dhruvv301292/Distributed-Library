import requests as req
import argparse
import time
import json
from concurrent.futures import ThreadPoolExecutor

messagestack = set()

class Client:
    def __init__(self, id, ip_dict):
        self.id = id
        self.ip_dict = ip_dict
        self.req_count = 1

    def connect(self, ip):
        try:
            print (req.get(ip).text)
        except:
            print("Server is not available")

    def trequestinfo(self, args):
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

    def tgetbook(self, args):
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


    def requestinfo(self, bookname):
        global messagestack
        with open ( 'members.txt', 'r' ) as f:
            members = json.load ( f )

        if len(members) == 0:
            print("No servers online")
            return

        member = members[0]
        inputargs = (self.ip_dict[member], self.id, member, bookname, self.req_count)

        response = self.trequestinfo(inputargs)


        if response[2] == "Server not available":
            print("Server not available")
        elif response[1] in messagestack:
            print ("request_num {}: Discarded duplicate reply from {}".format(response[1], response[0]))
        else:
            print ( "[{}] | Received <{}, {}, {}, Response: {}>".format (
            time.strftime("%H:%M:%S", time.localtime()), response[0], self.id, response[1], response[2]))
            messagestack.add(response[1])
        self.req_count += 1

    def getbook(self, bookname):
        global messagestack
        with open('members.txt', 'r') as f:
            members = json.load(f)

        if len(members) == 0:
            print("No servers online")
            return

        member = members[0]
        inputargs = (self.ip_dict[member], self.id, member, bookname, self.req_count)

        response = self.tgetbook(inputargs)

        if response[2] == "Server not available":
            print("Server not available")
        elif response[1] in messagestack:
            print("request_num {}: Discarded duplicate reply from {}".format(response[1], response[0]))
        else:
            print("[{}] | Received <{}, {}, {}, Response: {}>".format(
            time.strftime("%H:%M:%S", time.localtime()), response[0], self.id, response[1], response[2]))
            messagestack.add(response[1])
        self.req_count += 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser ()
    parser.add_argument('--id', type=str, default='C1')
    parser.add_argument('--ip1', type=str, default='http://127.0.0.1:5000/')
    parser.add_argument ('--ip2', type=str, default='http://127.0.0.1:5010/')
    parser.add_argument ('--ip3', type=str, default='http://127.0.0.1:5020/')
    args = parser.parse_args()


    com1 = args.ip1
    com2 = args.ip2
    com3 = args.ip3
    ip_dict = {"S1": com1, "S2": com2, "S3": com3}
    client = Client(args.id, ip_dict)

    client.connect(com1)
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
                client.requestinfo(reqlist[1])
            elif reqlist[0] == 'req' or reqlist[0] == 'request':
                client.getbook(reqlist[1])