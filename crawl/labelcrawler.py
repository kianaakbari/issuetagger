import requests
import json
from requests.auth import HTTPBasicAuth
from datetime import datetime
import time
import math
import sys

issue_label = "support"

delay_conn = 60
clients = [('your_clinet_id_1', 'your_clinet_secret_1'),
           ('your_clinet_id_2', 'your_clinet_secret_2'),
           ('your_clinet_id_3', 'your_clinet_secret_3'),
           ('your_clinet_id_4', 'your_clinet_secret_4'),
           ('your_clinet_id_5', 'your_clinet_secret_5')]
clients_number = len(clients)          
client_index = 0
headers = {}
headers['User-Agent'] = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"
headers['Accept'] = 'Accept: application/vnd.github.squirrel-girl-preview'

def get_data_pages(req_url, upper_bound=math.inf, key=-1):    
    page_number = 1
    resp_list = [] 
    
    while(page_number<=upper_bound):         
        try:   
            r = requests.get(req_url + "&page=" + str(page_number), headers=headers) 
            print(page_number)
            if(r.ok):                            
                result = json.loads(r.text or r.content)
                
                if key == -1: 
                    data = result                        
                else:
                    if not key in result:
                        print("key not exists")    
                        break                    
                    data = result[key]

                resp_list += data          
                if not data:
                    print("no data")
                    break
                page_number += 1
                    
                try:
                    if int(r.headers["X-RateLimit-Remaining"]) < 2:
                        print("limit exceeded!!!!!!!!!!!!")
                        delay = 60
                        print('sleeping for '+str(delay)+' seconds...')
                        print("current time:" + str(datetime.now()))
                        time.sleep(int(delay))
                except (KeyError):
                    pass            
            else:
                resp = json.loads(r.text or r.content)
                print('\n---'+str(r))
                print('\n---'+str(resp['message']))
                return False
        except requests.exceptions.Timeout as e:
            print("-------timeout-------")
            print(e)
            time.sleep(delay_conn)
            return get_data_pages(req_url, upper_bound, key)
        except requests.ConnectionError as e:
            print("-------connection error-------")
            print(e)
            time.sleep(delay_conn)
            return get_data_pages(req_url, upper_bound, key)
    return resp_list

start_time = datetime.now() 
last_date = '2020-10-15T10:23:19Z'
issues_list = []
batch_number = 1

while True:    
    print(f"batch number: {batch_number}")
    client_id, client_secret = clients[client_index]
    issues_req = 'https://api.github.com/search/issues?q=label:'+issue_label+'+state:closed+created:<'+last_date+\
                               '+language:java&sort=created&per_page=100&client_id=' + client_id + '&client_secret=' + client_secret
    print(issues_req)
    batch_issues_list = get_data_pages(issues_req, 10, "items")
    
    if not batch_issues_list:
        break
  
    client_index += 1
    if(client_index == clients_number):
        client_index = 0
        
    last_date = batch_issues_list[-1]["created_at"]
    issues_list += batch_issues_list
    batch_number += 1
    
end_time = datetime.now() 
duration = end_time - start_time
print("duration time " + str(duration)+"\n")

print(len(issues_list))


with open(f"{issue_label}_issues.txt", "w") as f:
    f.write(json.dumps(issues_list))