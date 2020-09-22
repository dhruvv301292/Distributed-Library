import requests as req
import time
import argparse

def heartbeat(ip, freq):
    start = time.time()
    check = True
    while check:
        try:
            resp = req.get(ip + "heartbeat")
            print(resp.text)
            time.sleep(freq - ((time.time() - start) % freq))
        except:
            check = False
            print("Server not available")

if __name__ == '__main__':
    parser = argparse.ArgumentParser ()
    parser.add_argument('--ip', type=str, default='http://127.0.0.1:5000/')
    parser.add_argument('--freq', type=float, default=1.0)
    args = parser.parse_args ()
    heartbeat(args.ip, args.freq)


