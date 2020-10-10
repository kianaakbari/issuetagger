import urllib.request
from bs4 import BeautifulSoup
import contextlib
import pandas as pd
import re
import numpy as np
import threading
import json

for repo in ['spring-boot', 'spring-framework', 'elasticsearch', 'RxJava', 'okhttp', 'retrofit', 'guava']:
    print(f"--------{repo}--------")
    with open(f"users/{repo}_users.txt") as f:
        x = f.read()
        users = json.loads(x)

    users_contribution = dict()
    org_users = []
    invalid_users = []
    unlucky_users = []
    others = []

    for i, user in enumerate(users):
        print(i)
        try:    
            with contextlib.closing(urllib.request.urlopen("https://github.com/" + user)) as page:
                soup = BeautifulSoup(page.read())       
                cntrb_section = soup.find_all("h2", {"class" : "f4 text-normal mb-2"})
                if cntrb_section:
                    users_contribution[user] = re.findall("[0-9,]* contribution", cntrb_section[0].text)[0][:-13]
                elif user == "ghost":
                    users_contribution[user] = 0
                else:
                    head_section = soup.find_all("a", {"class" : "pagehead-tabs-item"})
                    if head_section:                
                        org_users.append(user)
                    else:
                        print("some problem ouside exception for", user)
                        others.append(user)
                    users_contribution[user] = 0
        except Exception as e:
            users_contribution[user] = 0
            if(str(e) == "HTTP Error 429: too many requests" or str(e).startswith("<urlopen error")):
                unlucky_users.append(user)
            elif str(e) == "HTTP Error 404: Not Found":
                invalid_users.append(user)
            else: 
                others.append(user)
            print(str(e))
            print("user is", user)

    print("invalid: ", invalid_users)
    print("org: ", org_users)
    print("unlucky: ", unlucky_users)
    print("others: ", others)
    print(len(users), len(users_contribution))

    with open(f"cntrb/{repo}_github_cntrb.txt", 'w') as f:
        f.write(json.dumps(users_contribution, indent = 4))
