import requests as req
import argparse
import time
import pickle

def load_data():
    a_file = open('membership.pkl', "rb")
    output = pickle.load(a_file)
    a_file.close()
    return output

class Client:
    def __init__(self, id, ips):
        self.id = id
        self.collection = {}
        self.ips = ips
        self.num_server = len(ips)
        self.req_count = 1

    def connect(self):
        connected = False
        for i in range(self.num_server):
            try:
                resp = req.get(self.ips[i])
                connected = True
            except:
                print("Server", i+1,  "is not available")

        if connected:
            print(resp.text)


    def requestinfo(self, bookname):
        message_recieved = False
        message = []
        self.members = load_data()

        for i in range(self.num_server):
            if self.members[i]:
                self.sending_message(i, bookname, 'info')

                try:
                    requestString = self.ips[i] + "info?clientId=" + self.id + "&bookName=" + bookname + "&reqCount=" + str(self.req_count)
                    res = req.get(requestString)
                    message_recieved = True
                    message.append(res.text)
                    self.reciept_success(i)
                    
                except:
                    self.reciept_failed(i)
                    message.append(None)
            else:
                message.append(None)
                
        if message_recieved:
            done_printing = False

            for i, reply in enumerate(message):
                if reply != None and self.members[i]:
                    if done_printing != True:
                        self.print_message(i, reply)
                        done_printing = True
                        print_index = i
                    else:
                        if reply == message[print_index]:
                            print('Request:', self.req_count, '-- Discarded duplicate reply from Server:', i+1)
            
            self.req_count += 1


    def getbook(self, bookname):
        message_recieved = False
        message = []
        self.members = load_data()

        for i in range(self.num_server):
            if self.members[i]:
                self.sending_message(i, bookname, 'get')
                try:
                    res = req.get(self.ips[i] + "get?clientId=" + self.id + "&bookName=" + bookname + "&reqCount=" + str(self.req_count))
                    message_recieved = True
                    message.append(res.text)
                    self.reciept_success(i)

                except:
                    self.reciept_failed(i)
                    message.append(None)
                
        if message_recieved:
            done_printing = False

            for i, reply in enumerate(message):
                if reply != None and self.members[i]:
                    if done_printing != True:
                        self.print_message(i, reply)
                        done_printing = True
                        print_index = i
                    else:
                        if reply == message[print_index]:
                            print('Request:', self.req_count, '-- Discarded duplicate reply from Server:', i+1)

                else:
                    message.append(None)
            
            self.req_count += 1


    ###### METHODS DEFINING VARIOUS PRINTING OPERATIONS  ############
    def sending_message(self, i, bookname, method):
        print("[{}] | Sending <{}, S{}, {}, {} {}>".format ( time.strftime ( "%H:%M:%S", time.localtime () ), self.id, str(i+1),  self.req_count, method, bookname))

    def reciept_success(self, i):
        print("[{}] | Received <{}, S{}, {}, Response: {}>".format(time.strftime("%H:%M:%S", time.localtime()), self.id, str(i+1), self.req_count, "Recieved Response from S" + str(i+1)))

    def reciept_failed(self, i):
        print("[{}] | Received <{}, S{}, {}, Response: {}>".format(time.strftime("%H:%M:%S", time.localtime()), self.id, str(i+1), self.req_count, "Server " + str(i+1) + " not available"))

    def print_message(self, i, text):
        print()
        print ("[{}] | Recieved <{}, S{}, {}, Response: {}>".format(time.strftime("%H:%M:%S", time.localtime()), self.id, str(i+1), self.req_count, text))
        print()





if __name__ == '__main__':
    parser = argparse.ArgumentParser ()
    parser.add_argument('--id', type=str, default='C1')
    parser.add_argument('--ports', type=int, default=[5000, 5001, 5002], nargs='+')
    args = parser.parse_args ()

    #Get a list of all servers
    num_server = len(args.ports)
    ips = []
    for port in args.ports:
        ips.append('http://127.0.0.1:' + str(port) + '/')

    #Create Client object
    client = Client(args.id, ips)
    client.connect()

    #Open communication between server and client
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

  