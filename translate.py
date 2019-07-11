import json
import time
from tqdm import tqdm
import random
import re
import threading
import sys
import os
import sys
import copy

punct = '!"#$%&\'()*+-/:;<=>?@[\\]^_`{|}~'
def translating(mode, fname, ori, dev):
    files = os.listdir(mode)
    idx = []
    for file in files:
        if file.endswith('.json'):
            json_file = file.split('_')
            if json_file[0] == 'translated' and json_file[-1] == fname:
                idx.append(int(json_file[1]))
    for i, data in enumerate(tqdm(ori['data'])):
        if i > max(idx):
            #translator = Translator()
            rn = random.randint(1, 10)*0.5
            time.sleep(rn)
            for j, paragraphs in enumerate(data['paragraphs']):
                translated_context = translator.translate(dev['data'][i]['paragraphs'][j]['context'],src='en', dest='id')
                dev['data'][i]['paragraphs'][j]['context'] = translated_context.text
                for k, qas in enumerate(paragraphs['qas']):
                    rn = random.randint(1, 10)*0.5
                    time.sleep(rn)
                    translated_question = translator.translate(dev['data'][i]['paragraphs'][j]['qas'][k]['question'],src='en', dest='id')
                    dev['data'][i]['paragraphs'][j]['qas'][k]['question'] = translated_question.text
                    for l, q in enumerate(qas['answers']):
                        rn = random.randint(1, 10)*0.5
                        time.sleep(rn)
                        text = dev['data'][i]['paragraphs'][j]['qas'][k]['answers'][l]['text']
                        translated_answer = translator.translate(text, src='en', dest='id')
                        dev['data'][i]['paragraphs'][j]['qas'][k]['answers'][l]['text'] = translated_answer.text
            with open('{}/translated_{}_{}'.format(mode, i, fname), 'w') as f:
                json.dump(dev['data'][i], f)
                print("saved to {}/translated_{}_{}".format(mode, i, fname))
    return dev

def mergerAll(folder_name):
    merged = {}
    tmp, indexes = [], []
    for trans in os.listdir(folder_name):
        if trans.endswith('.json'):
            indexes.append(int(trans.split('_')[1]))
            with open(os.path.join(os.getcwd(), folder_name, trans), 'r') as f:
                data = json.load(f)
            tmp.append(data)
    merged['data'] = tmp
    fname = 'merged_{}_{}_{}.json'.format(min(indexes), max(indexes), folder_name)
    with open(fname, 'w') as f:
        json.dump(merged, f)
    return merged, fname

def matchingManually(folder_name):
    dataset, fname = mergerAll(folder_name)
    error = []
    results = []
    fname_split = fname.split('_')
    first = int(fname_split[1])
    last = int(fname_split[2])
    for i in range(first, last+1):
        for j, paragraphs in enumerate(dataset['data'][i-first]['paragraphs']):
            text = dataset['data'][i-first]['paragraphs'][j]['context']
            for k, qas in enumerate(paragraphs['qas']):
                for l, q in enumerate(qas['answers']):
                    word = dataset['data'][i-first]['paragraphs'][j]['qas'][k]['answers'][l]['text']
                    try:
                        st = re.search(word, text, re.IGNORECASE).start()
                        en = re.search(word, text, re.IGNORECASE).end()
                        results.append((text[st:en], word,
                                        dataset['data'][i-first]['paragraphs'][j]['qas'][k]['answers'][l]['answer_start']))
                    except:
                        with open('{}_output.txt'.format(fname[:-5]), 'r') as f:
                            matched = f.read().split('\n')
                        idxs = []
                        for idx in matched:
                            idxs.append(idx.split(' ')[0])
                        #print(idxs)
                        idxHere = str(i)+'_'+str(j)+'_'+str(k)+'_'+str(l)
                        if idxHere not in idxs:
                            print(idxHere)
                            question = qas['question']
                            print(text)
                            print(question)
                            print(word)
                            #print(answer)
                            new = input("new answer : ")
                            new = str(new)
                            if new != 'x':
                                with open('{}_output.txt'.format(fname[:-5]), "a+") as f:
                                    f.write(idxHere+" "+str(new)+os.linesep)
                            else:
                                pass
                        error.append((text, word))
    return results, error

def mergeWithManual(jsonFile, txtFile, minIdx, maxIdx, mode):
    if mode == 'train':
        m = 'train'
    elif mode == 'dev':
        m = 'dev'
    else:
        print('There are just two modes, train or dev')
        pass
    with open(jsonFile, 'r') as f:
        jsonFormat = json.load(f)
    with open(txtFile, 'r') as f:
        txtFormat = f.read()
    txtFormat = txtFormat.split('\n')[:-1]
    for manual in txtFormat:
        idx = manual.split(' ')[0].split('_')
        idx = list(map(int, idx))
        i, j, k, l = idx
        jsonFormat['data'][i]['paragraphs'][j]['qas'][k]['answers'][l]['text'] = " ".join(manual.split(' ')[1:])
    with open('{}_{}_{}.json'.format(m,minIdx, maxIdx), 'w') as f:
        clean = {}
        clean['data'] = jsonFormat['data'][minIdx:maxIdx+1]
        json.dump(clean, f)

    return jsonFormat

def errorCheck(fname):
    with open(fname, 'r') as f:
        data = json.load(f)
    dataset = copy.deepcopy(data)
    error = []
    results = []
    #fname = fname[:-5]
    #fname_split = fname.split('_')
    #first = int(fname_split[1])
    #last = int(fname_split[2])
    for i, data in tqdm(enumerate(dataset['data'])):
        for j, paragraphs in enumerate(data['paragraphs']):
            text = dataset['data'][i]['paragraphs'][j]['context']
            for k, qas in enumerate(paragraphs['qas']):
                try:
                    for l, q in enumerate(qas['answers']):
                        word = dataset['data'][i]['paragraphs'][j]['qas'][k]['answers'][l]['text']
                        try:
                            start = re.search(word, text, re.IGNORECASE).start()
                            end = re.search(word, text, re.IGNORECASE).end()
                            dataset['data'][i]['paragraphs'][j]['qas'][k]['answers'][l]['answer_start'] = start
                            dataset['data'][i]['paragraphs'][j]['qas'][k]['answers'][l]['text'] = text[start:end]
                            #results.append((text[start:end], word,
                            #                dataset['data'][i]['paragraphs'][j]['qas'][k]['answers'][l]['answer_start']))
                        except (AttributeError, ValueError):
                            idxs = []
                            for p in punct:
                                a = word.find(p)
                                if a != -1:
                                    idxs.append(a)
                            try:
                                new_word = word[:min(idxs)]
                                start = re.search(new_word, text, re.IGNORECASE).start()
                                end = re.search(new_word, text, re.IGNORECASE).end()
                                dataset['data'][i]['paragraphs'][j]['qas'][k]['answers'][l]['answer_start'] = start
                            except:
                                pass
                            #results.append((text[start:end], word,
                            #                dataset['data'][i]['paragraphs'][j]['qas'][k]['answers'][l]['answer_start']))

                        except:
                            pass
                            # print("Unexpected error:", sys.exc_info()[0])
                            # answer = dataset['data'][i]['paragraphs'][j]['qas'][k]['answers'][l]['text']#['answer_start']
                            # error.append((str(i)+'_'+str(j)+'_'+str(k)+'_'+str(l), text, qas['question'], answer))
                except:
                    pass
    return dataset, error

def matchingRegexError(jsonFile, errors):
    i = 0
    with open(jsonFile, 'r') as f:
        dataset = json.load(f)
    for error in errors:
        idxs = error[0].split('_')
        idxs = list(map(int, idxs))
        i, j, k, l = idxs
        text = dataset['data'][i]['paragraphs'][j]['context']
        answer = dataset['data'][i]['paragraphs'][j]['qas'][k]['answers'][l]
        print(text)
        print(answer,'\n')
        new_answer = input("find word or sentence : ")
        start = re.search(new_answer, text, re.IGNORECASE).start()
        print("are you sure to save index new start at {}?".format(start))
        save = input()
        if save == 'y' or save == 'yes':
            dataset['data'][i]['paragraphs'][j]['qas'][k]['answers'][l]['answer_start'] = start
            i = i + 1
        elif save == 'n' or save == 'no':
            print('save index manually')
            idx_manual = input()
            dataset['data'][i]['paragraphs'][j]['qas'][k]['answers'][l]['answer_start'] = int(idx_manual)
        else:
            pass

    print('done {} annotation from {} errors'.format(i, len(errors)))
    return dataset


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'matching':
            folder_name = input("whats folder you want matching? : ")
            matchingManually(str(folder_name))
        else:
            print('are you wanna translating?')
            pass
    else:
        mode = input("mode : ")
        if mode == 'train':
            fname = 'train-v1.1.json'
        elif mode == 'dev':
            fname = 'dev-v1.1.json'
        else:
            print('There are just two modes, train or dev')
            pass
        from googletrans import Translator
        translate_urls = ["translate.google.com", "translate.google.co.kr",
                              "translate.google.co.id", "translate.google.de",
                              "translate.google.ru", "translate.google.ch",
                              "translate.google.fr", "translate.google.es"]
        translator= Translator(service_urls=translate_urls)
        with open(fname, 'rb') as f:
            train = json.load(f)
        threading.Thread(target=translating(mode, fname, train.copy(), train)).start()
