from flask import Flask, request
import time
import argparse

app = Flask(__name__)

library = {}
library["Asterix"] = 5
library["Harry Potter"] = 7
library["Dune"] = 3

serverid = 1

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
    clientid = request.args.get('clientId')
    bookName = request.args.get('bookName')
    reqCount = request.args.get('reqCount')
    print ("[{}] | Received <{}, {}, {}, Request: info {}>".format ( time.strftime ( "%H:%M:%S", time.localtime () ), clientid, args.id, reqCount, bookName))
    print ("State before processing <{}, {}, {}, Request: info {}>:".format(clientid, args.id, reqCount, bookName) + str(library))
    if bookName in library.keys() and library.get(bookName) != 0:
        infoString = "Yes! {} copy/copies of {} available!".format(library.get(bookName), bookName)
        print ("State after processing <{}, {}, {}, Request: info {}>:".format(clientid, args.id, reqCount, bookName) + str(library))
        print ("[{}] | Sending <{}, {}, {}, Response: {}>".format ( time.strftime ( "%H:%M:%S", time.localtime () ),clientid, args.id, reqCount, infoString))
        return infoString

    else:
        infoString = "Sorry! {} is not available at the moment.".format(bookName)
        print ( "State after processing <{}, {}, {}, Request: info {}>:".format(clientid, args.id, reqCount, bookName) + str(library))
        print ( "[{}] | Sending <{}, {}, {}, Response: {}>".format(time.strftime("%H:%M:%S", time.localtime () ), clientid, args.id, reqCount, infoString))
        return infoString



@app.route("/get/")
def getBook():
    clientid = request.args.get('clientId')
    bookName = request.args.get('bookName')
    reqCount = request.args.get('reqCount')
    print ( "[{}] | Received <{}, {}, {}, Request: get {}>".format ( time.strftime ( "%H:%M:%S", time.localtime () ), clientid, args.id, reqCount, bookName ) )
    print ( "State before processing <{},{}, {}, Request: get {}>:".format ( clientid, args.id, reqCount, bookName ) + str (library ) )
    if bookName in library.keys() and library.get(bookName) != 0:
        library[bookName] = library.get(bookName) - 1
        getString = "Yes! {} has been shared with you! {} more copy/copies available!".format(bookName, library.get(bookName))
        print("State after processing <{}, {}, {}, Request: info {}>:".format ( clientid, args.id, reqCount, bookName ) + str(library))
        print("[{}] | Sending <{}, {}, {}, Response: {}>".format ( time.strftime ( "%H:%M:%S", time.localtime () ), clientid, args.id, reqCount, getString))
        return getString

    else:
        infoString = "Sorry! {} is not available at the moment.".format ( bookName )
        print ( "State after processing <{}, {}, {}, Request: info {}>:".format ( clientid, args.id, reqCount, bookName ) + str(library))
        print ( "[{}] | Sending <{}, {}, {}, Response: {}>".format ( time.strftime ( "%H:%M:%S", time.localtime () ), clientid, args.id, reqCount, infoString ) )
        return infoString


if __name__ == "__main__":
    parser = argparse.ArgumentParser ()
    parser.add_argument('--id', type=str, default='S1')
    parser.add_argument('--port', type=int, default=5000)
    args = parser.parse_args ()
    app.run(debug=True, port=args.port)
