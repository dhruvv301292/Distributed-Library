import requests as req
import time
import argparse
import pickle



def save_data(data):
    #Storing data with labels
    a_file = open('rm_membership_rm.pkl', "wb")
    pickle.dump(data, a_file)
    a_file.close()

class RM:
    def __init__(self, ips, freq):
        self.heartbeat_count = 0
        self.ips = ips
        self.num_server = len(ips)
        self.alive = [False]*self.num_server 
        self.freq = freq
        print('RM:', sum(self.alive), 'members\n')
        save_data(self.alive)

    def heartbeat(self):
        start = time.time()
        check = True

        while check:
            self.heartbeat_count += 1

            #TODO: remove heartbeat for RM
            
            for i, ip in enumerate(self.ips):
                print ( "[{}] | beatCount: {} sending heartbeat".format (time.strftime ( "%H:%M:%S", time.localtime () ), self.heartbeat_count ) )

                try:
                    resp = req.get(ip + "heartbeat")
                    print("[{}] | beatCount: {} | received response from GFD{}: {}".format(time.strftime("%H:%M:%S", time.localtime()), self.heartbeat_count, i+1, resp.text))
                    if resp.text == 'True' and self.alive[i] != True:
                        self.alive[i] = True
                        print('Added Member S' + str(i+1) )
                    elif resp.text == 'False' and self.alive[i] != False:
                        self.alive[i] = False

                except:
                    print("[{}] | beatCount: {}: GFD not available".format (time.strftime("%H:%M:%S", time.localtime()), self.heartbeat_count))
                    self.alive[i] = False

            alive_members = ['S'+str(i) for i in range(len(self.alive)) if self.alive[i] == True]
            members = ",".join(alive_members)
            print('RM:', sum(self.alive), 'members:', members,'\n')
            time.sleep ( self.freq - ((time.time () - start) % self.freq) )
            save_data(self.alive)
            print()

if __name__ == '__main__':
    parser = argparse.ArgumentParser ()
    parser.add_argument('--ports', type=int, default=[5020], nargs='+') # port number of GFD will be 5020 here.
    parser.add_argument('--freq', type=float, default=1.0)
    args = parser.parse_args ()

    #Get a list of all servers
    num_server = len(args.ports)
    ips = []
    for port in args.ports:
        ips.append('http://127.0.0.1:' + str(port) + '/')
    print(ips)
    
    rm = RM(ips, args.freq)
    rm.heartbeat()
