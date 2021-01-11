import requests as req
import argparse
import time
import json


messagestack = set()

class Client:
    def __init__(self, id, ip_dict):
        self.id = id
        self.ip_dict = ip_dict
        self.req_count = 1

    def connect(self):
        self.ip_dict["S1"].connect()

    def requestinfo(self, bookname):
        global messagestack
        with open ( 'members.txt', 'r' ) as f:
            members = json.load ( f )
        if len(members) == 0:
            print("No servers online")
            return
        responses = []
        for member in members:
            responses.append ( self.ip_dict[member].requestinfo ( bookname, self.req_count ) )
        for response in responses:
            if response[2] == "Server not available":
                continue
            elif response[1] in messagestack:
                print ( "request_num {}: Discarded duplicate reply from {}".format ( response[1], response[0] ) )
            else:
                print ( "[{}] | Received <{}, {}, {}, Response: {}>".format (
                    time.strftime ( "%H:%M:%S", time.localtime () ), response[0], self.id, response[1], response[2] ) )
                messagestack.add ( response[1] )
        self.req_count += 1

    def getbook(self, bookname):
        with open ( 'members.txt', 'r' ) as f:
            members = json.load(f)
        for member in members:
            ip_dict[member].getbook(bookname, self.req_count)
        self.req_count += 1

class serverCom:
    def __init__(self, id, serverid, ip):
        self.id = id
        self.serverid = serverid
        self.ip = ip

    def connect(self):
        try:
            print(req.get(self.ip).text)
        except:
            print("Server is not available")

    def requestinfo(self, bookname, req_count):
        # global messagestack
        print ( "[{}] | Sending <{}, {}, {}, info {}>".format ( time.strftime ( "%H:%M:%S", time.localtime () ),
                                                                self.serverid, self.id, req_count, bookname ) )
        try:
            requestString = self.ip + "info?clientId=" + self.id + "&bookName=" + bookname + "&reqCount=" + str (
                req_count )
            res = req.get ( requestString )
            # if req_count in messagestack:
            #     print("request_num {}: Discarded duplicate reply from {}".format(req_count, self.serverid))
            # else:
            #     print ("[{}] | Received <{}, {}, {}, Response: {}>".format(time.strftime("%H:%M:%S", time.localtime()), self.serverid, self.id, req_count, res.text))
            #     messagestack.add(req_count)
            return self.serverid, req_count, res.text
        except:
            return self.serverid, req_count, "Server not available"
            # print("[{}] | Received <{}, {}, {}, Response: {}>".format(time.strftime("%H:%M:%S", time.localtime()), self.serverid, self.id, req_count, "Server not available"))

    def getbook(self, bookname, req_count):
        global messagestack
        print("[{}] | Sending <{}, {}, {}, get {}>".format(time.strftime("%H:%M:%S", time.localtime()), self.serverid, self.id, req_count, bookname ) )
        try:
            res = req.get(self.ip + "get?clientId=" + self.id + "&bookName=" + bookname + "&reqCount=" + str(req_count))
            if req_count in messagestack:
                print ("request_num {}: Discarded duplicate reply from {}".format(req_count, self.serverid))
            else:
                print("[{}] | Received <{}, {}, {}, Response: {}>".format(time.strftime("%H:%M:%S", time.localtime()), self.serverid, self.id, req_count, res.text))
                messagestack.add(req_count)
        except:
            print("[{}] | Received <{}, {}, {}, Response: {}>".format(time.strftime("%H:%M:%S", time.localtime()), self.serverid, self.id, req_count, "Server not available"))

if __name__ == '__main__':
    parser = argparse.ArgumentParser ()
    parser.add_argument('--id', type=str, default='C1')
    parser.add_argument('--ip1', type=str, default='http://127.0.0.1:5000/')
    parser.add_argument ('--ip2', type=str, default='http://127.0.0.1:5010/')
    parser.add_argument ('--ip3', type=str, default='http://127.0.0.1:5020/')
    args = parser.parse_args()


    com1 = serverCom(args.id, "S1", args.ip1)
    com2 = serverCom(args.id, "S2", args.ip2)
    com3 = serverCom(args.id, "S3", args.ip3)
    ip_dict = {"S1": com1, "S2": com2, "S3": com3}
    client = Client(args.id, ip_dict)

    client.connect ()
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

