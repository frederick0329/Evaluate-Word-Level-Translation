from __future__ import print_function
import sys
import os
import numpy as np
import codecs
import argparse
import enchant
en_dict = enchant.Dict("en_US")

def prettyPrint(translation1_f1, translation1_precision, translation1_recall, translation2_f1, translation2_precision, translation2_recall):
    names = ['translation1', 'translation2']
    name_width = max(len(cn) for cn in names)
    
    digits = 3
    width = max(name_width, digits)
  
    headers = ["f1-score", "precision", "recall"]
    head_fmt = u'{:>{width}s} ' + u' {:>9}' * len(headers) + u' \n'
    report = head_fmt.format(u'', *headers, width=width)

    report += u'\n'

    f1 = [translation1_f1, translation2_f1]
    p = [translation1_precision, translation2_precision]
    r = [translation1_recall, translation2_recall]

    row_fmt = u'{:>{width}s} ' + u' {:>9.{digits}f}' * 3 + u' \n'
    rows = zip(names, f1, p, r)
    for row in rows:
        report += row_fmt.format(*row, width=width, digits=digits)

    

    report += u'\n'

    report += row_fmt.format('delta',
                             translation1_f1 - translation2_f1,
                             translation1_precision - translation2_precision,
                             translation1_recall - translation2_recall,
                             width=width, digits=digits)

    print(report)

def calculateScore(align_path, src_path, ref_path, translation1_path, translation2_path, word_list):
    translation1_score = {}
    translation2_score = {}

    align_lines = codecs.open(align_path, 'r', 'UTF-8').readlines()
    num_lines = int(len(align_lines) / 3)
    
    src_lines = codecs.open(src_path, 'r', 'UTF-8').readlines()
    ref_lines = codecs.open(ref_path, 'r', 'UTF-8').readlines()
    translation1_lines = codecs.open(translation1_path, 'r', 'UTF-8').readlines()
    translation2_lines = codecs.open(translation2_path, 'r', 'UTF-8').readlines()

    ref_align_lines = align_lines[:num_lines]
    translation1_align_lines = align_lines[num_lines:num_lines * 2]
    translation2_align_lines = align_lines[num_lines * 2:]
    


    for i, line in enumerate(src_lines):
        tokens = line.split()
        ref_tokens = ref_lines[i].split()
        translation1_tokens = translation1_lines[i].split()
        translation2_tokens = translation2_lines[i].split()
        
        for token_idx, token in enumerate(tokens):
            token = token.lower()
            # Only calculate words in the given list
            if token in word_list:
                if token not in translation1_score:
                    translation1_score[token] = [0, 0, 0]
                    translation2_score[token] = [0, 0, 0]

                ref_align_tokens = [ref_tokens[int(x.split('-')[1])].lower() for x in ref_align_lines[i].split() if int(x.split('-')[0]) == token_idx]
                translation1_align_tokens = [translation1_tokens[int(x.split('-')[1])].lower() for x in translation1_align_lines[i].split() if int(x.split('-')[0]) == token_idx]
                translation2_align_tokens = [translation2_tokens[int(x.split('-')[1])].lower() for x in translation2_align_lines[i].split() if int(x.split('-')[0]) == token_idx]
                # Calculate Matches
                if len(ref_align_tokens) > 0:
                    # translation1_tp 
                    translation1_score[token][0] += len([x for x in translation1_align_tokens if x in ref_align_tokens])
                    # translation1_tp_fp 
                    translation1_score[token][1] += len(translation1_align_tokens)
                    # translation1_tp_fn 
                    translation1_score[token][2] += len(ref_align_tokens)
                    # translation2_tp 
                    translation2_score[token][0] += len([x for x in translation2_align_tokens if x in ref_align_tokens])
                    # translation2_tp_fp 
                    translation2_score[token][1] += len(translation2_align_tokens)
                    # translation2_tp_fn 
                    translation2_score[token][2] += len(ref_align_tokens)
                     
    translation1_tp = 0
    translation1_tp_fp = 0
    translation1_tp_fn = 0
    translation2_tp = 0
    translation2_tp_fp = 0
    translation2_tp_fn = 0
      
    for token in translation1_score:
        translation1_tp +=  translation1_score[token][0]               
        translation1_tp_fp +=  translation1_score[token][1]               
        translation1_tp_fn +=  translation1_score[token][2]               
        translation2_tp +=  translation2_score[token][0]               
        translation2_tp_fp +=  translation2_score[token][1]               
        translation2_tp_fn +=  translation2_score[token][2]         
    
    translation1_precision = translation1_tp * 1.0 / translation1_tp_fp   
    translation1_recall = translation1_tp * 1.0 / translation1_tp_fn
    translation1_f1 = 2 * translation1_precision * translation1_recall / (translation1_precision + translation1_recall)
    translation2_precision = translation2_tp * 1.0 / translation2_tp_fp   
    translation2_recall = translation2_tp * 1.0 / translation2_tp_fn
    translation2_f1 = 2 * translation2_precision * translation2_recall / (translation2_precision + translation2_recall)

    prettyPrint(translation1_f1, translation1_precision, translation1_recall, translation2_f1, translation2_precision, translation2_recall)

def getAllWordList(dict_path):
    tgt_dict_lines = codecs.open(dict_path, 'r', 'UTF-8').readlines()
    words = []
    for line in tgt_dict_lines[:]:
        word = line.split()[0]
        word = word.lower()
        if not en_dict.check(word):
            continue
        words.append(word)
    return words

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--align_path", help="alignment file path (output of fast_align)",type=str)
    parser.add_argument("-s", "--src_path", help="source of test file",type=str)
    parser.add_argument("-r", "--ref_path", help="reference of test file",type=str)
    parser.add_argument("-t1", "--trans1_path", help="translation of first model",type=str)
    parser.add_argument("-t2", "--trans2_path", help="translation of second model",type=str)
    parser.add_argument("-w", "--word_list_path", help="path to a list of words to evaluate on",type=str)
    args = parser.parse_args()  
    '''
    tgt_lang = 'zh'
    dict_path = '/home/chieh/emnlp/OpenNMT/wmt_en_' + tgt_lang + '/preprocessed.src.dict'
    
    src_path = '/home/chieh/emnlp/OpenNMT/data_fast_align/en'+tgt_lang+'/newstest.en'
    ref_path = '/home/chieh/emnlp/OpenNMT/data_fast_align/en'+tgt_lang+'/newstest.'+tgt_lang
    translation1_path = '/home/chieh/emnlp/OpenNMT/data_fast_align/en'+tgt_lang+'/baseline.txt' 
    translation2_path = '/home/chieh/emnlp/OpenNMT/data_fast_align/en'+tgt_lang+'/biencoder.txt'
    align_path = '/home/chieh/emnlp/OpenNMT/data_fast_align/en'+tgt_lang+'/test.align'
    #print(word_list)
    homo_path = '/home/chieh/emnlp/OpenNMT/homograph.lst'
    '''
    align_path = args.align_path
    src_path = args.src_path
    ref_path = args.ref_path
    translation1_path = args.trans1_path
    translation2_path = args.trans2_path
    word_list_path = args.word_list_path

    word_list = getAllWordList(word_list_path)
    calculateScore(align_path, src_path, ref_path, translation1_path, translation2_path, word_list)
if __name__ == '__main__':
  main()  

