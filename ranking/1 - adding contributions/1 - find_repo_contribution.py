import requests
import json
import pandas as pd
import numpy as np
from requests.auth import HTTPBasicAuth
from datetime import datetime
import time
import re
import sys
import numpy as np

delay_conn = 60
clients = [('your_clinet_id_1', 'your_clinet_secret_1'),
           ('your_clinet_id_2', 'your_clinet_secret_2'),
           ('...', '...')]
clients_number = len(clients)          
client_index = 0
headers = {}
headers['Accept'] = 'application/vnd.github.starfox-preview+json'

unnormal_requests = []
def get_data_pages(req_url):    
    page_number = 1
    resp_list = [] 
    
    while(True):
        number_of_tries = 10
        try:   
            r = requests.get(req_url + "&page=" + str(page_number), headers=headers)            
            if(r.ok):  
                if r.status_code == 200:
                    result = json.loads(r.text or r.content)
                    resp_list += result            

                    if not result:
                        break

                    if(len(result)<100):
                        break

                    page_number += 1

                    # check for max limit
                    try:
                        if int(r.headers["X-RateLimit-Remaining"]) < 10:
                            print("limit exceeded!!!!!!!!!!!!")
                            delay = float(r.headers["X-RateLimit-Reset"]) - time.mktime(time.localtime())#.total_seconds()
                            print('sleeping for '+str(delay)+' seconds...')
                            print("current time:" + str(datetime.now()))
                            time.sleep(int(delay))
                    except (KeyError):
                        pass        
                else:
                    unnormal_requests.append(req_url)
                    return False,0
            else:
                j = json.loads(r.text or r.content)
                print('\n---'+str(r))
                print('\n---'+str(j['message']))
                return False,0
        except requests.exceptions.Timeout as e:
            print("-------timeout-------")
            print(e)
            number_of_tries-=1
            if(number_of_tries):
                time.sleep(delay_conn)
                get_data_pages(req_url)
            else:
                sys.exit(1)
        except requests.ConnectionError as e:
            print("-------connection error-------")
            print(e)
            number_of_tries-=1
            if(number_of_tries):
                time.sleep(delay_conn)
                get_data_pages(req_url)
            else:
                sys.exit(1)
    return resp_list, page_number


with open("repo_addresses.txt") as f:
    repo_addresses = json.loads(f.read())
    
repos_dict = {}
counter = 0
start_time = datetime.now()

for repo_address in repo_addresses:
    print(repo_address)
    
    repo_name = repo_address.split('/')[1]
    
    client_id, client_secret = clients[client_index]
    req = f"https://api.github.com/repos/{repo_address}/contributors?per_page=100&client_id={client_id}&client_secret={client_secret}"
    cntrb_obj, num_of_pages = get_data_pages(req)
    
    if cntrb_obj:
        counter += num_of_pages
        client_index += 1
        if(client_index == clients_number):
            client_index = 0

        if counter == 5000*clients_number:
            end_time = datetime.now()
            duration = (end_time - start_time).seconds
            if(duration < 3600):
                time.sleep(3600 - duration)
                print(f"sleep for {3600 - duration} seconds")
            counter = 0
            start_time = datetime.now()

        d = dict()
        for i in cntrb_obj:
            d[i["login"]] = i["contributions"]

        repos_dict[repo_name] = d
    
with open(f"data/repo_cntrb.txt", 'w') as f:
    f.write(json.dumps(repos_dict , indent = 4))
    
print("---finished---")

print(unnormal_requests)