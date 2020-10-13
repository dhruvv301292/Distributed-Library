from flask import Flask, request
import requests as req
import time
import argparse
import threading

ALIVE = False

app = Flask(__name__)

@app.route("/heartbeat")
def heartbeat():
    print()
    print("[{}] Heartbeat received from GFD".format(time.strftime("%H:%M:%S", time.localtime())))
    print ( "[{}] Sending response to GFD".format ( time.strftime ( "%H:%M:%S", time.localtime () )) )

    return str(ALIVE)


class LFD:
    def __init__(self, id, ip, freq):
        self.heartbeat_count = 1
        self.id = id
        self.ip = ip
        self.freq = freq

    def heartbeat(self):
        print()
        start = time.time()
        check = True
        global ALIVE

        while check:
            print ( "[{}] | beatCount: {} | {} sending heartbeat".format (time.strftime ( "%H:%M:%S", time.localtime () ), self.heartbeat_count, self.id ) )
            try:
                resp = req.get(self.ip + "heartbeat/" + self.id)
                print("[{}] | beatCount: {} | {} received response: {}".format(time.strftime("%H:%M:%S", time.localtime()), self.heartbeat_count, self.id, resp.text))
                ALIVE = True

            except:
                print("[{}] | beatCount: {} | {}: Server not available".format (time.strftime("%H:%M:%S", time.localtime()), self.heartbeat_count, self.id))
                ALIVE = False
                
            self.heartbeat_count += 1
            time.sleep ( self.freq - ((time.time () - start) % self.freq) )
            print()

def heartbeat_replicas(lfd):
    lfd.heartbeat()


if __name__ == '__main__':
    parser = argparse.ArgumentParser ()
    parser.add_argument('--id', type=str, default='lfd1')
    parser.add_argument('--serverport', type=str, default='5010')
    parser.add_argument('--launchport', type=int, default='5000')
    parser.add_argument('--freq', type=float, default=1.0)
    args = parser.parse_args ()

    #Heartbeat replicas in a separate thread
    ip = 'http://127.0.0.1:' + args.serverport + '/'
    lfd = LFD(args.id, ip, args.freq)
    x = threading.Thread(target=heartbeat_replicas, args=(lfd,))
    x.start()

    #Launch LFD
    app.run(debug=False, port=args.launchport)


