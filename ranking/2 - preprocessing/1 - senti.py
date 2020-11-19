from sentistrength import PySentiStr
import pandas as pd
from textblob import TextBlob

df = pd.read_csv("prioritization/data/allrepos_processed_textonly.csv")
df['title_processed'] = df['title_processed'].astype(str)
df['body_processed'] = df['body_processed'].astype(str)

senti = PySentiStr()
senti.setSentiStrengthPath('/home/ubuntu/Kiana/data/SentiStrength.jar')  # Note: Provide absolute path instead of relative path
senti.setSentiStrengthLanguageFolderPath('/home/ubuntu/Kiana/data/SentiStrength_Data/')  # Note: Provide absolute path instead of relative path

def sentistrength(txt):
    sentiments = senti.getSentiment(txt, score='binary')[0]
    print(sentiments)
    return str(sentiments[0])+","+str(sentiments[1])

print("*****senti started title*****")
df["title_sentistrenght"] = df['title_processed'].apply(sentistrength)
print("*****senti started title*****")
df["body_sentistrenght"] = df['body_processed'].apply(sentistrength)

def textblob(txt):
    b = TextBlob(txt)
    s = b.sentiment
    return str(s[0])+","+str(s[1])

print("*****blob started title*****")
df["title_textblob"] = df['title_processed'].apply(textblob)
print("*****blob started body*****")
df["body_textblob"] = df['body_processed'].apply(textblob)

sentiment_columns = ["title_sentistrenght", "body_sentistrenght", "title_textblob", "body_textblob"]
df[sentiment_columns].to_csv("prioritization/data/allrepos_sentiments.csv", index=False)

