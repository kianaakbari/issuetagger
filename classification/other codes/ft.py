import pandas as pd
import fasttext

def classify(file_name, tune,  wngram=1, column_postfix="_processed"):
    df = pd.read_csv(f"../data/{file_name}_textonly.csv")
    df[f"title{column_postfix}"]  = df[f"title{column_postfix}"].astype(str)
    df[f"body{column_postfix}"]  = df[f"body{column_postfix}"].astype(str)
    df["text"] = df[f"title{column_postfix}"] + " " + df[f"body{column_postfix}"]
    
    train = df[df["test_tag"]==0]
    valid = df[df["test_tag"]==1]

    train_target = list(train["label_cat"])
    train_txt = list(train["text"])
    train_size = train.shape[0]
    f = open("../data/train.txt","w",encoding="utf-8")
    for i in range(train_size):
        f.write("__label__" + train_target[i] + " " + train_txt[i] + "\n")
    f.close()

    valid_target = list(valid["label_cat"])
    valid_txt = list(valid["text"])
    valid_size = valid.shape[0]
    f = open("../data/validation.txt","w",encoding="utf-8")
    for i in range(valid_size):
        f.write("__label__" + valid_target[i] + " " + valid_txt[i] + "\n")
    f.close()
    
    if tune:
        model = fasttext.train_supervised(input='../data/train.txt', autotuneValidationFile='../data/validation.txt', autotuneDuration=36000)
    else:
        model = fasttext.train_supervised(input="../data/train.txt", wordNgrams=wngram)
    postfix = column_postfix.strip("_")
    
    result_file = f"results/ft--{file_name}--tuned.txt" if tune else f"results/ft--{file_name}--ngram{wngram}.txt"
    result = open(result_file,"w")
    result.write(str(model.test("../data/validation.txt")))
    result.write("\n")
    result.write(str(model.test_label("../data/validation.txt")))
    result.close()

classify("clean_mono_norm", 1)
