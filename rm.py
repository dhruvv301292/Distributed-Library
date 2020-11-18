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



if __name__ == '__main__':
    parser = argparse.ArgumentParser ()
    parser.add_argument('--port', type=int, default=5020) # port number of GFD will be 5020 here.
    parser.add_argument('--freq', type=float, default=1.0)
#     parser.add_argument('--servers', type=int, default=[5000]) # list of all server ports

    args = parser.parse_args()

    app.run(debug=False, port=args.port)
