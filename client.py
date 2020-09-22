import requests as req
import argparse

def connect(ip):
    try:
        print(req.get(ip).text)
    except:
        print("Server is not available")

def requestinfo(ip, bookname):
    # try:
    requestString = ip + "info/" + bookname
    res = req.get(requestString)
    print(res.text)
    # except:
    #     print("Server is not available")

def requestbook(ip, bookname):
    try:
        res = req.get(ip + "get/" + bookname)
        print(res.text)
    except:
        print("Server is not available")

if __name__ == '__main__':
    parser = argparse.ArgumentParser ()
    parser.add_argument('--ip', type=str, default='http://127.0.0.1:5000/')
    parser.add_argument('--num_clients', type=int, default=3)
    args = parser.parse_args ()
    connect(args.ip)
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
                requestinfo(args.ip, reqlist[1])
            elif reqlist[0] == 'req' or reqlist[0] == 'request':
                requestbook(args.ip, reqlist[1])

