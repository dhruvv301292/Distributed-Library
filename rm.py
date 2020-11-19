import requests as req
import time
import argparse
import pickle
from flask import Flask, request
import requests as req


app = Flask(__name__)
new_member = -1 

servers = {'S1':'http://127.0.0.1:5000/','S2': 'http://127.0.0.1:5001/', 'S3':'http://127.0.0.1:5002/'}

def save_data(data):
    #Storing data with labels
    a_file = open('membership_rm.pkl', "wb")
    pickle.dump(data, a_file)
    a_file.close()


@app.route('/update')
def updateRM():
    members = request.args.get('members')
    members = members.split(',')
    member_count = request.args.get('memberCount')
    new_member = request.args.get('new')
    dead_members = request.args.get('dead')
    dead_members = dead_members.split(',')
    print("RM:{} members: {}".format(member_count, members))
    save_data(members)
    print('='*10)

    
    if int(new_member) != -1:
        print("Send checkpoint to this server: ", dead_members)
        new_member = 'S' + new_member
        replicas = set(members) - set(new_member)
        print("Replicas:",list(replicas))
    
    
        
        for r in list(replicas):
            try:
                checkpoint_alert = servers.get(r)+"watchtower?"+"new="+new_member+"&inform="+r
                signal = req.get(checkpoint_alert)
                print("Response of server:",r, signal.text)

            except:
                print("Connection with server {} is closed.".format(r))

    return "RM received update"


def rm_init():
    print ("RM: 0 members")

if __name__ == '__main__':
    parser = argparse.ArgumentParser ()
    parser.add_argument('--port', type=int, default=5020) # port number of GFD will be 5020 here.
    parser.add_argument('--freq', type=float, default=1.0)
    parser.add_argument('--servers', type=int, default=[5000]) # list of all server ports

    args = parser.parse_args()


    rm_init()
    app.run(debug=False, port=args.port)

    

   