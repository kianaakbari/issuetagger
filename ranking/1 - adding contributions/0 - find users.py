import pandas as pd
import json

users = []

with open("repos.txt") as f:
    repos = json.loads(f.read())
    
for repo in repos:
    df = pd.read_csv(f"data/{repo}.csv")
    users += list(df.author_login)
    users += list(df.closer_login)
    
with open("data/userslist.txt", "w") as f:
    f.write(json.dumps(list(set(users))))
    
