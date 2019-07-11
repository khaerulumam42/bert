"""
This code use for delete inequality between ground truth of text asnwer
and text index in context. The data will be remove

"""


import json
import copy

def checking(jsonFile):
    # jsonFile = string > path directory json file
    
    inequal = 0
    examples = []
    with open(jsonFile, 'r') as f:
        data = json.load(f)
    tmp = copy.deepcopy(data)
    for i, datum in enumerate(data['data']):
        for j, paragraphs in enumerate(datum['paragraphs']):
            context = paragraphs['context']
            for k, qas in enumerate(paragraphs['qas']):
                # for l, answer in enumerate(qas['answers']):
                word = qas['answers'][0]['text']
                start = qas['answers'][0]['answer_start']
                if not word == context[start:start+len(word)]:
                    # [k-inequal] use for avoid out of range index some element on the list has been removed
                    tmp['data'][i]['paragraphs'][j]['qas'].remove(tmp['data'][i]['paragraphs'][j]['qas'][k-inequal])
                    examples.append("{} vs {}".format(word, context[start:start+len(word)]))
                    inequal += 1
    
    return inequal, examples, tmp

if __name__ == "__main__":
    outputs = ['dataset/final_train_lenna_v3.0.json', 'dataset/final_dev_lenna_v3.0.json']
    for i, fname in enumerate(['dataset/tmp_train_lenna_v3.0.json', 'dataset/tmp_dev_lenna_v3.0.json']):
        inequal, examples, tmp = checking(fname)
        print("there are {} inequal between answer and context in {}, this is the examples".format(len(examples),fname))
        # for i in range(len(examples)):
        #     print(examples[i])
        
        with open(outputs[i], 'w') as f:
            json.dump(tmp, f)

