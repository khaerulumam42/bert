import json
import random
import translate
import string
import secrets
import pandas as pd
from ast import literal_eval
from datetime import datetime
import os
from tqdm import tqdm

punct = '!"#$%&\'()*+-/:;<=>?@[\\]^_`{|}~'


def cleaning(txtFile):
    cleaned = []
    for line in txtFile:
        if line != '\n':
            if line.split('\n')[-1] == '':
                cleaned.append(line.split('\n')[0])
    return cleaned

def whatIs(list_):
    if list_[:8] == 'title : ':
        return 'title'
    elif list_[:4] == 'q : ':
        return 'question'
    elif list_[:4] == 'a : ':
        return 'answer'
    else:
        return 'text'
    
    return None

def toDataset(outputFile, txtFile):
    # init dict file for final output
    er = 0
    dict_ = {}
    dict_['version'] = '3.0'
    dict_['data'] = ''
    # clean from \n char to separate each line
    deleteEnter = cleaning(txtFile)
    title, q, a, t = None, None, None, None
    whole, qas, = [], []
    for i, structure in enumerate(tqdm(deleteEnter)):
        # for last iteration
        if i == len(deleteEnter)-1:
            paragraphs['paragraphs'] = paragraph
            paragraphs['title'] = title
            whole.append(paragraphs)
        # if see the 'title'
        elif whatIs(structure) == 'title':
            # if meet new title, add last data
            if title != None:
                paragraphs['paragraphs'] = paragraph
                paragraphs['title'] = title
                whole.append(paragraphs)
            # and reinitiate variable
            paragraph, paragraphs = [], {}
            title = structure[8:]
        # if structure is text
        elif whatIs(structure) == 'text':
            context, qas = {}, []
            t = structure  
        # question part
        elif whatIs(structure) == 'question':            
            qa = {}
            q = structure[4:]
            # TODO : create real id
            qa['id'] = secrets.token_hex(20)
            qa['question'] = q
            #if i <= len(deleteEnter)-4:
            answers = []
            for j in range(1, 4):
                answer = {}
                # answer start get from next process, so initiate first
                answer['answer_start'] = ''
                if deleteEnter[i+j][:4] == 'a : ':
                    answer['text'] = deleteEnter[i+j][4:]
                    answers.append(answer)
                else:
                    answer['text'] = deleteEnter[i+1][4:]
                    answers.append(answer)
            qa['answers'] = answers
            qas.append(qa)
            if i <= len(deleteEnter)-5:
                if whatIs(deleteEnter[i+4]) == 'title' or whatIs(deleteEnter[i+4]) == 'text':
                    # print(whatIs(deleteEnter[i+4]))
                    # print(structure)
                    # print(t)
                    # print(title)
                    context['context'] = t
                    context['qas'] = qas
                    paragraph.append(context)
                    assert paragraph != []
        else:
            pass
            
    dict_['data'] = whole
    with open(outputFile, 'w') as f:
        json.dump(dict_, f)
    return dict_

def splitDataset(jsonFile, train_rat=0.8):
    with open(jsonFile, 'r') as f:
        dataset = json.load(f)
    data_train, data_dev = [], []
    train, dev = {}, {}
    train['version'] = dataset['version']
    dev['version'] = dataset['version']
    for i, paragraphs in enumerate(dataset['data']):
        para_train, para_dev = {}, {}
        title = paragraphs['title']
        train_data, dev_data = [], []
        length = len(paragraphs['paragraphs'])
        length_rnd = random.sample(range(length), length)
        train_idxs = length_rnd[:int(train_rat*length)]
        dev_idxs = length_rnd[int(train_rat*length):]
        for j in train_idxs:
            train_data.append(paragraphs['paragraphs'][j])
        for j in dev_idxs:
            dev_data.append(paragraphs['paragraphs'][j])
        para_train['title'] = title
        para_train['paragraphs'] = train_data
        para_dev['title'] = title
        para_dev['paragraphs'] = dev_data
        
        data_train.append(para_train)
        data_dev.append(para_dev)
        
    train['data'] = data_train
    dev['data'] = data_dev
    train_name = 'dataset/train_lenna_v{}.json'.format(train['version'])
    dev_name = 'dataset/dev_lenna_v{}.json'.format(dev['version'])
    with open(train_name, 'w') as f:
        json.dump(train, f)
    with open(dev_name, 'w') as f:
        json.dump(dev, f)
    train_res, train_err = translate.errorCheck(train_name)
    dev_res, dev_err = translate.errorCheck(dev_name)
    print('train error {}, dev error {}'.format(len(train_err), len(dev_err)))
    return train, dev, train_err, dev_err, train_name, dev_name

def processFolder(folder):
    created = []
    for fname in os.listdir(folder):
        created.append(fname+'\n')
        with open(os.path.join(folder, fname), 'r') as f:
            created.extend(f.readlines())
            created.append('\n')
    return created

def processFile(filename):
    with open(filename, 'r') as f:
        created= f.readlines()
    return created


def convert(folderInput):
    created = processFolder(folderInput)
    d = toDataset('lennaQA.json', created)

    train, dev, train_err, dev_err, train_name, dev_name = splitDataset('lennaQA.json', train_rat=0.8)
    for jsonFile in [train_name, dev_name]:
        results, errors = translate.errorCheck(jsonFile)
        with open('dataset/tmp_{}'.format(jsonFile.split('/')[-1]), 'w') as f:
            json.dump(results, f)
            # print(results)
            print("save file into {}".format('dataset/tmp_'+jsonFile.split('/')[-1]))
    
    print("all process done!")
    
if __name__ == "__main__":
    convert('dataset/trainTxt')
