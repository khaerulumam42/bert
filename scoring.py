import json
import re
from ast import literal_eval

def fromBucket(directory):
    # directory : string > path of file in bucket storage
    bucket_name = re.search(r"gs://(.*?)/", directory).group(1)
    from google.cloud import storage
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blob = bucket.get_blob(directory.replace('gs://{}/'.format(bucket_name), ''))
    return blob.download_as_string()

def openFile(devFile, predFile):
    # identify storage is local or bucket
    if devFile[:5] == 'gs://':
        dev = literal_eval(fromBucket(devFile))
    else:
        with open(devFile, 'r') as f:
            dev = json.load(f)
    
    if predFile[:5] == 'gs://':
        pred = literal_eval(fromBucket(predFile))
    else:
        with open(predFile, 'r') as f:
            pred = json.load(f)
    
    return dev, pred

def flattenDev(devJson):
    # convert SQuAD formatting into flat dictionary format on dev file
    # devJson : json-like format (dictionary)
    flatten = {}
    for datum in devJson['data']:
        for paragraph in datum['paragraphs']:
            for qas in paragraph['qas']:
                qid = qas['id']
                answers  = []
                for answer in qas['answers']:
                    answers.append(answer['text'])
                    
                flatten[qid] = answers
    
    return flatten

def score(flatDev, flatPred):
    # initiate scoring
    # EM = exact matching is when the answers is same with first answer on three answer
    # f1 = if answer from model in between 3 answers provide in dev, it calculate as True prediction
    EM, f1, count = 0, 0, 0

    # looping for key(qas id) to see what answer by model in flatPred
    for key in flatPred.keys():
        # use set to avoid double adding score, bcs sometimes 
        # there are same answers is more than 1 in 3 answers
        count += 1
        for i, answer in enumerate(set(flatDev[key])):
            if flatPred[key].lower() == answer.lower():
                EM += 1
                f1 += 1
            elif flatPred[key].lower() in answer.lower() or answer.lower() in flatPred[key].lower():
                f1 += 1
            else:
                pass
    
    EM = EM*100/count
    f1 = f1*100/count
    return EM, f1

def calculate(devFile, predFile):
    dev, pred = openFile(devFile, predFile)
    dev = flattenDev(dev)
    EM, f1 = score(dev, pred)
    return EM, f1
