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

# last_issue_numbers = {"spring-projects/spring-boot": 18689, "spring-projects/spring-framework": 23840, "elastic/elasticsearch": 48295}
last_issue_numbers = {"ReactiveX/RxJava": 7092, "square/okhttp": 6308, "square/retrofit": 3475, "google/guava":5263}
repos = last_issue_numbers.keys()

delay_conn = 10
clients = [('your_clinet_id_1', 'your_clinet_secret_1'),
           ('your_clinet_id_2', 'your_clinet_secret_2'),
           ('your_clinet_id_3', 'your_clinet_secret_3'),
           ('your_clinet_id_4', 'your_clinet_secret_4'),
           ('your_clinet_id_5', 'your_clinet_secret_5')]

clients_number = len(clients)          
headers = {}
headers['Accept'] = 'application/vnd.github.starfox-preview+json'

#chunk_size = rate_limit*clients_number/requests_per_issue
#rate_limit = 5000
#clients_number = 5
#requests_per_issue =~ 5 #chon axare issue ha bishtar az 100 ta cm ya event nadaran, baraye taghirban hamashun bishtar az 5 ta req dade nmishe
chunk_size = 5000

def get_data(req_url):
    number_of_tries = 10
    try:   
        r = requests.get(req_url, headers=headers)
        if(r.ok):            
            result = json.loads(r.text or r.content)            
            
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
            
            return result
        
        else:
            j = json.loads(r.text or r.content)
            print('\n---'+str(r))
            print('\n---'+str(j['message']))
            return False
    except requests.exceptions.Timeout as e:
        print("-------timeout-------")
        print(e)
        number_of_tries-=1
        if(number_of_tries):
            time.sleep(delay_conn)
            get_data(req_url)
        else:
            sys.exit(1)
    except requests.ConnectionError as e:
        print("-------connection error-------")
        print(e)
        number_of_tries-=1
        if(number_of_tries):
            time.sleep(delay_conn)
            get_data(req_url)
        else:
            sys.exit(1)

def get_data_pages(req_url):    
    page_number = 1
    resp_list = [] 
    
    while(True):         
        number_of_tries = 10
        try:   
            r = requests.get(req_url + "&page=" + str(page_number), headers=headers)            
            if(r.ok):                            
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
                j = json.loads(r.text or r.content)
                print('\n---'+str(r))
                print('\n---'+str(j['message']))
                return False
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
    return resp_list

def get_issues(repo_address):
    client_index = 0
    repo_name = repo_address.split('/')[1]
    df_size = last_issue_numbers[repo_address]
    chunks_number = df_size//chunk_size if df_size//chunk_size == df_size/chunk_size else df_size//chunk_size+1
    numbers = list(range(1,df_size+1))
    
    for i in range(chunks_number):
        print("****chunk number: " + str(i) + "****")
        batch_start_time = datetime.now()
        issues = []
        for number in numbers[i*chunk_size:(i+1)*chunk_size]:
            client_id, client_secret = clients[client_index]

            issue_req = "https://api.github.com/repos/" + repo_address + "/issues/" + str(number) + "?client_id=" + client_id + "&client_secret=" + client_secret  
            issue_obj = get_data(issue_req)
            
            if issue_obj:
                closer_obj = np.nan
                if issue_obj["closed_by"]:
                    closer = issue_obj["closed_by"]["login"]
                    user_req = "https://api.github.com/users/" + closer + '?client_id=' + client_id + '&client_secret=' + client_secret
                    closer_obj = get_data(user_req)        


                author = issue_obj["user"]["login"]
                user_req = "https://api.github.com/users/" + author + '?client_id=' + client_id + '&client_secret=' + client_secret
                author_obj = get_data(user_req)

                events_req = "https://api.github.com/repos/" +  repo_address + "/issues/" + str(number) + "/events?per_page=100" + '&client_id=' + client_id + '&client_secret=' + client_secret
                events_obj = get_data_pages(events_req)

                comments_req = "https://api.github.com/repos/" + repo_address + "/issues/" + str(number) + "/comments?per_page=100" + '&client_id=' + client_id + '&client_secret=' + client_secret
                comments_obj = get_data_pages(comments_req)

            client_index += 1
            if(client_index == clients_number):
                client_index = 0 

            if(issue_obj == False or closer_obj == False or author_obj == False or events_obj == False or comments_obj==False):
                print("\n-------some problem with this issue!-------")
            else:
                issues.append({"number":number, "issue_obj":json.dumps(issue_obj), "author_obj":json.dumps(author_obj), "closer_obj":json.dumps(closer_obj), "events_obj":json.dumps(events_obj), "comments_obj":json.dumps(comments_obj)})
        issues_df = pd.DataFrame(issues)
        issues_df.to_csv("data/"+repo_name+"_"+str(i)+".csv", index=False)
        print("------batch "+str(i+1)+" completed------")
        batch_end_time = datetime.now()
        duration = (batch_end_time - batch_start_time).seconds
        if(duration < 3600 and i != chunks_number):
            print("----sleep time: " + str(duration) + "----")
            time.sleep(3600 - duration)
            
     
for repo_address in repos:
    print("---------repo_address---------")
    print("Starting time:" + str(datetime.now()))
    get_issues(repo_address)
    print("End time:" + str(datetime.now()))
