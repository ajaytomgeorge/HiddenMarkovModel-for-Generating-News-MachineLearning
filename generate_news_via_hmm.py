import math
import numpy as np
import os
import pandas as pd
import pickle
import random
import re
import string
import nltk
nltk.download('punkt')

from datetime import datetime
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords



column_names = ["source", "agent", "goal", "data","methods", "results", "issues", "score", "comments"]

def initialize():
    directory = os.fsencode("./data")
    output = pd.DataFrame()
    faulty=0
    """Loads the all file into memory, corrects issues with different no of '=' with appropriate regex"""                  
    for file in os.listdir(directory):
        try:
            filename = os.fsdecode(file)
            df = open(os.path.join(os.getcwd(),"data",filename), "r")
            lines = df.readlines()
            row={}
            for line in lines:
                current_line = line.replace("\n", "")
                try:
                    if current_line.startswith('=') and any([re.sub(r'\W+', '', current_line).lower()==name for name in column_names]):
                        section = re.sub(r'\W+', '', current_line).lower()
                        row[section]= ''
                    elif current_line!= ' \n':
                        row[section]= row[section]+" "+ current_line
                except Exception as e:
                    faulty+=1
                    break
            df.close()
            output = output.append(row, ignore_index=True)
        except Exception:
                faulty+=1
        
    print("Initialization Complete")
    return output

def picklyfy(data):
    """pickle the object so that we done need to preprocess the file each time we run"""
    data_file = open("processed_data.pickle", "wb")
    pickle.dump(data,data_file, protocol=pickle.HIGHEST_PROTOCOL)
    data_file.close()
    
def fetch_saved():
    data_file = open("processed_data.pickle", "rb")
    data = pickle.load(data_file)
    data_file.close()
    return data

def clean(txt):
    '''Further Clean the data of any special symbols and tokenise it'''
    cleaned_txt = []
    for line in txt:
        if isinstance(line, str):
            line = line.lower() 
            line = re.sub(r"[,.\"\'!@#$%^&*(){}?/;`~:<>+=-\\]", "", line)
            tokens = word_tokenize(line)
            words = [word for word in tokens if word.isalpha()]
            cleaned_txt+=words
    return cleaned_txt


def make_markov_model(cleaned_stories, n_gram=2):
    """Make our markow model, n_gram is to add context to our words"""
    markov_model = {}
    for i in range(len(cleaned_stories)-n_gram-1):
        curr_state, next_state = "", ""
        for j in range(n_gram):
            curr_state += cleaned_stories[i+j] + " "
            next_state += cleaned_stories[i+j+n_gram] + " "
        curr_state = curr_state[:-1]
        next_state = next_state[:-1]
        if curr_state not in markov_model:
            markov_model[curr_state] = {}
            markov_model[curr_state][next_state] = 1
        else:
            if next_state in markov_model[curr_state]:
                markov_model[curr_state][next_state] += 1
            else:
                markov_model[curr_state][next_state] = 1
    
    # calculating transition probabilities
    for curr_state, transition in markov_model.items():
        total = sum(transition.values())
        for state, count in transition.items():
            markov_model[curr_state][state] = count/total
        
    return markov_model


def generate_story(markov_model, limit=random.randint(10, 100), start='is very'):
    n = 0
    curr_state = start
    next_state = None
    story = ""
    story+=curr_state+" "
    while n<limit:
        try:
            curr_state = list(markov_model.keys())[1] if curr_state not in markov_model.keys() else curr_state
            next_state = random.choices(list(markov_model[curr_state].keys()),
                                    list(markov_model[curr_state].values()))
        except Exception as e:
            continue
            
        curr_state = next_state[0]
        story+=curr_state+" "
        n+=1
    return story
    
if __name__=="__main__":
    processed_data=initialize()
    markov_models={}
    for name in column_names:
        markov_models[name]= make_markov_model(clean(processed_data[name]))
    print("Cleaning Complete")
    # picklyfy(markov_models)
    # markov_models= fetch_saved()
    start = {"source":"the source", "agent":"the document", "goal":"goal is", "data":"the data", "methods":
        "the methodology", "results":"the results", "issues":"human involvement", "score":"although im", "comments":"the article"}    
    for i in range(10):
        filename=datetime.now().strftime("%Y-%m-%d_%I-%M-%S_%p")
        f= open(f"Sample Generated_news {i}{filename} ","w+")
        for name in column_names:
            f.write(f"== {name.upper()}\n")
            f.write(f"{generate_story(markov_models[name], start=start[name])} \n")
            f.write("\n")
        f.close()
            
        
    print("10 Files generated successfully ")
            
            
        
      