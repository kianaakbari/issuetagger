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

delay_conn = 10
headers = {}
headers['Accept'] = 'application/vnd.github.starfox-preview+json'

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


for repo_address in ['spring-projects/spring-boot', 'spring-projects/spring-framework', 'elastic/elasticsearch', 'ReactiveX/RxJava', 'square/okhttp', 'square/retrofit', 'google/guava']:
    repo_name = repo_address.split('/')[1]
    print(repo_name)
    req = f"https://api.github.com/repos/{repo_address}/contributors?per_page=100"
    cntrb_obj = get_data_pages(req)
    
    d = dict()
    for i in cntrb_obj:
        d[i["login"]] = i["contributions"]
    
    with open(f"cntrb/{repo_name}_repo_cntrb.txt", 'w') as f:
        f.write(json.dumps(d , indent = 4))
    
print("---finished---")