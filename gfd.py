import requests as req
import time
import argparse
import pickle

def save_data(data):
    #Storing data with labels
    a_file = open('membership.pkl', "wb")
    pickle.dump(data, a_file)
    a_file.close()



class GFD:
    def __init__(self, ips, freq, rm):
        self.heartbeat_count = 0
        self.ips = ips
        self.num_server = len(ips)
        self.alive = [False]*self.num_server 
        self.freq = freq
        self.rm = rm
        print('GFD:', sum(self.alive), 'members\n')
        save_data(self.alive)


        
    def heartbeat(self):
        start = time.time()
        check = True
        
        while check:
            self.heartbeat_count += 1
            new_member = -1

            for i, ip in enumerate(self.ips):
                print ( "[{}] | beatCount: {} sending heartbeat".format (time.strftime ( "%H:%M:%S", time.localtime () ), self.heartbeat_count ) )
                
                try:
                    resp = req.get(ip + "heartbeat")
                    print("[{}] | beatCount: {} | received response from lfd{}: {}".format(time.strftime("%H:%M:%S", time.localtime()), self.heartbeat_count, i+1, resp.text))
                    if resp.text == 'True' and self.alive[i] != True:
                        self.alive[i] = True
                        print('Added Member S' + str(i+1) )
                        new_member = i+1


                    elif resp.text == 'False' and self.alive[i] != False:
                        self.alive[i] = False

                except:
                    print("[{}] | beatCount: {}: lfd{} not available".format (time.strftime("%H:%M:%S", time.localtime()), self.heartbeat_count, i+1))
                    self.alive[i] = False


            alive_members = ['S'+str(i+1) for i in range(len(self.alive)) if self.alive[i] == True]
            members = ",".join(alive_members)
            print('GFD:', sum(self.alive), 'members:', members,'\n')
            time.sleep ( self.freq - ((time.time () - start) % self.freq) )
            save_data(self.alive)

            #TODO: Send update from GFD to RM heresnt .
            dead_members = [str(i+1) for i in range(len(self.alive)) if self.alive[i] == False]
            dead_members = ",".join(dead_members)
            rm_update = self.rm+"update?memberCount="+str(sum(self.alive))+"&members="+members+"&new="+str(new_member)+"&dead="+dead_members
            rm_response = req.get(rm_update)
            # print(rm_response.text)
            
            


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    #TODO: setup port number for GFD to RM

    parser.add_argument('--ports', type=int, default=[5010, 5011, 5012], nargs='+')
    parser.add_argument('--freq', type=float, default=1.0)
    parser.add_argument('--rm', type=int, default=5020)
    args = parser.parse_args ()

    #Get a list of all servers
    num_server = len(args.ports)
    ips = []
    for port in args.ports:
        ips.append('http://127.0.0.1:' + str(port) + '/')
    print(ips)

    rm = 'http://127.0.0.1:' + str(args.rm) + '/'

    gfd = GFD(ips, args.freq, rm)
    gfd.heartbeat()


