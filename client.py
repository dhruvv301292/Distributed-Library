import requests as req
import argparse
import time

class Client:
    def __init__(self, id, ip):
        self.id = id
        self.collection = {}
        self.ip = ip
        self.req_count = 1

    def connect(self):
        try:
            print(req.get(self.ip).text)
        except:
            print("Server is not available")

    def requestinfo(self, bookname):
        print("[{}] | Sending <{}, S1, {}, info {}>".format ( time.strftime ( "%H:%M:%S", time.localtime () ), self.id, self.req_count, bookname))
        try:
            requestString = self.ip + "info?clientId=" + self.id + "&bookName=" + bookname + "&reqCount=" + str(self.req_count)
            res = req.get(requestString)
            print ("[{}] | Received <{}, S1, {}, Response: {}>".format(time.strftime("%H:%M:%S", time.localtime()), self.id, self.req_count, res.text))
            self.req_count += 1
        except:
            print("[{}] | Received <{}, S1, {}, Response: {}>".format(time.strftime("%H:%M:%S", time.localtime()), self.id, self.req_count, "Server not available"))

    def getbook(self, bookname):
        print("[{}] | Sending <{}, S1, {}, get {}>".format(time.strftime("%H:%M:%S", time.localtime()), self.id, self.req_count, bookname ) )
        try:
            res = req.get(self.ip + "get?clientId=" + self.id + "&bookName=" + bookname + "&reqCount=" + str(self.req_count))
            print("[{}] | Received <{}, S1, {}, Response: {}>".format(time.strftime("%H:%M:%S", time.localtime()), self.id, self.req_count, res.text))
            self.req_count += 1
        except:
            print("[{}] | Received <{}, S1, {}, Response: {}>".format(time.strftime("%H:%M:%S", time.localtime()), self.id, self.req_count, "Server not available"))

if __name__ == '__main__':
    parser = argparse.ArgumentParser ()
    parser.add_argument('--id', type=str, default='C1')
    parser.add_argument('--ip', type=str, default='http://127.0.0.1:5000/')
    args = parser.parse_args ()

    client = Client(args.id, args.ip)
    client.connect()
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

    # [timestamp] Sent <C1, S1, 101, request>
    # print ( "[{}] | beatCount: {} | {} sending heartbeat to S1".format (time.strftime ( "%H:%M:%S", time.localtime () ), self.heartbeat_count, self.id ) )

