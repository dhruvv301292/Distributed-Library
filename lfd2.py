from flask import Flask, request
import time
import requests as req
import argparse
import threading
import logging

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.disabled = True
app.logger.disabled = True

connected = False

@app.route("/gfdbeat")
def test():
    global connected
    if connected:
        return "Alive"
    else:
        return "Dead"

def heartbeat(id, ip, freq):
    start = time.time ()
    heartbeat_count = 1
    startcount = 0
    global connected
    gfdthread = threading.Thread ( target=startGFD )
    while True:
        if heartbeat_count == 1 or connected:
            print("[{}] | beatCount: {} | {} sending heartbeat to S1".format(time.strftime ( "%H:%M:%S", time.localtime () ), heartbeat_count, id))
        try:
            # resp = req.get ( ip + "heartbeat/" + id )
            resp = req.get ( ip + "heartbeat?id=" + id + "&count=" + str(heartbeat_count))
            if startcount == 0:
                gfdthread.start()
                startcount += 1
            connected = True
            print("[{}] | beatCount: {} | {} received response from S1: {}".format(time.strftime("%H:%M:%S", time.localtime()), heartbeat_count, id, resp.text))
            heartbeat_count += 1
            time.sleep(freq - ((time.time() - start) % freq))
        except:
            if connected:
                print ( "[{}] | beatCount: {} | {}: Server not available".format (
                time.strftime ( "%H:%M:%S", time.localtime () ), heartbeat_count, id))
                connected = False
            elif not connected and heartbeat_count == 1:
                print ( "[{}] | beatCount: {} | {}: Server not available".format (
                    time.strftime ( "%H:%M:%S", time.localtime () ), heartbeat_count, id ) )
                heartbeat_count += 1
            time.sleep ( freq - ((time.time () - start) % freq) )

def startGFD():
    app.run (debug=False, host="127.0.0.1", port=args.port)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--id', type=str, default='lfd1')
    parser.add_argument('--port', type=int, default=5002)
    parser.add_argument('--sip', type=str, default='http://127.0.0.1:5000/')
    parser.add_argument('--freq', type=float, default=1.0)
    args = parser.parse_args ()
    x = threading.Thread ( target=heartbeat, args=(args.id, args.sip, args.freq))
    x.start()
    # app.run ( debug=False, host="127.0.0.1", port=args.port )