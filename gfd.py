import requests as req
import time
import argparse


class GFD:
    def __init__(self, ips, freq):
        self.heartbeat_count = 0
        self.ips = ips
        self.num_server = len(ips)
        self.alive = [False]*self.num_server 
        self.freq = freq
        print('GFD:', sum(self.alive), 'members\n')
        
    def heartbeat(self):
        start = time.time()
        check = True

        while check:
            self.heartbeat_count += 1
            
            for i, ip in enumerate(self.ips):
                print ( "[{}] | beatCount: {} sending heartbeat".format (time.strftime ( "%H:%M:%S", time.localtime () ), self.heartbeat_count ) )
                
                try:
                    resp = req.get(ip + "heartbeat")
                    print("[{}] | beatCount: {} | received response from lfd{}: {}".format(time.strftime("%H:%M:%S", time.localtime()), self.heartbeat_count, i+1, resp.text))
                    if resp.text == 'True' and self.alive[i] != True:
                        self.alive[i] = True
                        print('Added Member S' + str(i+1) )
                    elif resp.text == 'False' and self.alive[i] != False:
                        self.alive[i] = False

                except:
                    print("[{}] | beatCount: {}: lfd{} not available".format (time.strftime("%H:%M:%S", time.localtime()), self.heartbeat_count, i+1))
                    self.alive[i] = False


            print('GFD:', sum(self.alive), 'members\n')
            time.sleep ( self.freq - ((time.time () - start) % self.freq) )
            print()

def heartbeat_replicas(lfd):
    lfd.heartbeat()


if __name__ == '__main__':
    parser = argparse.ArgumentParser ()
    parser.add_argument('--ports', type=list, default=[5010, 5011, 5012])
    parser.add_argument('--freq', type=float, default=1.0)
    args = parser.parse_args ()

    #Get a list of all servers
    num_server = len(args.ports)
    ips = []
    for port in args.ports:
        ips.append('http://127.0.0.1:' + str(port) + '/')

    gfd = GFD(ips, args.freq)
    gfd.heartbeat()


