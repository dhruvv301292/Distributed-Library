import requests as req
import time
import argparse


class LFD:
    def __init__(self, id, ip, freq):
        self.heartbeat_count = 1
        self.id = id
        self.ip = ip
        self.freq = freq

    def heartbeat(self):
        start = time.time()
        check = True
        while True:
            if check:
                print ( "[{}] | beatCount: {} | {} sending heartbeat to S1".format (time.strftime ( "%H:%M:%S", time.localtime () ), self.heartbeat_count, self.id ) )
            try:
                resp = req.get(self.ip + "heartbeat/" + self.id)
                print("[{}] | beatCount: {} | {} received response from S1: {}".format(time.strftime("%H:%M:%S", time.localtime()), self.heartbeat_count, self.id, resp.text))
                self.heartbeat_count += 1
                check = True
                time.sleep(self.freq - ((time.time() - start) % self.freq))
            except:
                if check:
                    print("[{}] | beatCount: {} | {}: Server not available".format (time.strftime("%H:%M:%S", time.localtime()), self.heartbeat_count, self.id))
                    self.heartbeat_count += 1
                    check = False
                time.sleep ( self.freq - ((time.time () - start) % self.freq) )

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--id', type=str, default='lfd1')
    parser.add_argument('--ip', type=str, default='http://127.0.0.1:5002/')
    parser.add_argument('--freq', type=float, default=1.0)
    args = parser.parse_args ()
    lfd = LFD(args.id, args.ip, args.freq)
    lfd.heartbeat()


