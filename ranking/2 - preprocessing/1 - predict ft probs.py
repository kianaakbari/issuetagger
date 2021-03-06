import fasttext
import pandas as pd

model = fasttext.load_model("tuned-30h.bin")
print("model is loaded")

df = pd.read_csv("data/allrepos_processed_textonly.csv")

df['title_processed'] = df['title_processed'].astype(str)
df['body_processed']= df['body_processed'].astype(str)
df['txt'] = df['title_processed'] + " " + df['body_processed']

l = list(df['txt'])
print("data is loaded")

prediction = model.predict(l, k=3)
print("prediction is completed")

labels, probabilities = prediction[0], prediction[1]
myzip = list(zip(labels, probabilities))
probsDict = list(map(lambda x: dict(zip(x[0],x[1])), myzip))
probsDf = pd.DataFrame(probsDict)

probsDf.to_csv("data/allrepos_ftprobs.csv", index=False)
print("finished")

