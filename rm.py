import requests as req
import time
import argparse
import pickle
from flask import Flask, request
import requests as req


app = Flask(__name__)
new_member = -1 

servers = {'0':'http://127.0.0.1:5000/','1': 'http://127.0.0.1:5001/', '2':'http://127.0.0.1:5002/'}

def save_data(data):
    #Storing data with labels
    a_file = open('membership_rm.pkl', "wb")
    pickle.dump(data, a_file)
    a_file.close()


@app.route('/update')
def updateRM():
    members = request.args.get('members')
    member_count = request.args.get('memberCount')
    new_member = request.args.get('new')

    print("RM:{} members: {}".format(member_count, members))
    save_data(members)
    
    
    if int(new_member) != -1:
        print("Send checkpoint to this server:", new_member)
        replicas = set(servers.keys()) - set((new_member))
        print(replicas)
        for r in list(replicas):
            checkpoint_alert = servers.get(r)+"watchtower?"+"new="+new_member+"&inform="+r
            signal = req.get(checkpoint_alert)
            print("Response of server:",r, signal.text)


    return "RM received update"



#Not using this class.
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
                # print ( "[{}] | beatCount: {} sending heartbeat".format (time.strftime ( "%H:%M:%S", time.localtime () ), self.heartbeat_count ) )

                try:
                    resp = request.get(ip + "heartbeat")
                    print("[{}] | beatCount: {} | received response from GFD{}: {}".format(time.strftime("%H:%M:%S", time.localtime()), self.heartbeat_count, i+1, resp.text))
                    print("Got response from GFD:", resp.text)
                    
                    if resp.text == 'True' and self.alive[i] != True:
                        self.alive[i] = True
                        print('Added Member S' + str(i+1) )
                    elif resp.text == 'False' and self.alive[i] != False:
                        self.alive[i] = False

                except:
                    print("[{}] | beatCount: {}: GFD not available".format (time.strftime("%H:%M:%S", time.localtime()), self.heartbeat_count))
                    # self.alive[i] = False

            alive_members = ['S'+str(i) for i in range(len(self.alive)) if self.alive[i] == True]
            members = ",".join(alive_members)
            print('RM:', sum(self.alive), 'members:', members,'\n')
            time.sleep ( self.freq - ((time.time () - start) % self.freq) )
            save_data(self.alive)
            print()

if __name__ == '__main__':
    parser = argparse.ArgumentParser ()
    parser.add_argument('--port', type=int, default=5020) # port number of GFD will be 5020 here.
    parser.add_argument('--freq', type=float, default=1.0)
    parser.add_argument('--servers', type=int, default=[5000]) # list of all server ports

    args = parser.parse_args()

    #Get a list of all servers
    # num_server = len(args.servers)
    # ips = []
    # for port in args.ports:
    #     ips.append('http://127.0.0.1:' + str(port) + '/')
    # print("Replicas available",ips)
    
    # rm = RM(ips, args.freq)
    # rm.heartbeat()

    app.run(debug=False, port=args.port)
