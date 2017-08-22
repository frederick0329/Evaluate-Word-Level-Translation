from __future__ import print_function
import sys
import os
import codecs
import argparse

def prettyPrint(translation_f1s, translation_precisions, translation_recalls):
    names = []
    for i in range(len(translation_f1s)):
        names.append('translation_' + str(i))

    name_width = max(len(cn) for cn in names)
    
    digits = 3
    width = max(name_width, digits)
  
    headers = ["f1-score", "precision", "recall"]
    head_fmt = u'{:>{width}s} ' + u' {:>9}' * len(headers) + u' \n'
    report = head_fmt.format(u'', *headers, width=width)

    report += u'\n'


    row_fmt = u'{:>{width}s} ' + u' {:>9.{digits}f}' * 3 + u' \n'
    rows = zip(names, translation_f1s, translation_precisions, translation_recalls)
    for row in rows:
        report += row_fmt.format(*row, width=width, digits=digits)

    report += u'\n'
    
    print(report)

def calculateScore(ref_align_path, translation_align_paths, src_path, ref_path, translation_paths, word_list):

    ref_align_lines = codecs.open(ref_align_path, 'r', 'UTF-8').readlines()
    
    src_lines = codecs.open(src_path, 'r', 'UTF-8').readlines()
    ref_lines = codecs.open(ref_path, 'r', 'UTF-8').readlines()
    
    translation_precisions = []
    translation_recalls = []
    translation_f1s = []
    for translation_path, translation_align_path in zip(translation_paths, translation_align_paths):
        translation_score = {}
        translation_lines = codecs.open(translation_path, 'r', 'UTF-8').readlines()
        translation_align_lines = codecs.open(translation_align_path, 'r', 'UTF-8').readlines()

        for i, line in enumerate(src_lines):
            tokens = line.split()
            ref_tokens = ref_lines[i].split()
            translation_tokens = translation_lines[i].split()
        
            for token_idx, token in enumerate(tokens):
                token = token.lower()
                # Only calculate words in the given list 
                if token in word_list:
                    if token not in translation_score:
                        translation_score[token] = [0, 0, 0]

                    ref_align_tokens = [ref_tokens[int(x.split('-')[1])].lower() for x in ref_align_lines[i].split() if int(x.split('-')[0]) == token_idx]
                    translation_align_tokens = [translation_tokens[int(x.split('-')[1])].lower() for x in translation_align_lines[i].split() if int(x.split('-')[0]) == token_idx]
                    # Calculate Matches
                    if len(ref_align_tokens) > 0:
                        # translation_tp 
                        translation_score[token][0] += len([x for x in translation_align_tokens if x in ref_align_tokens])
                        # translation_tp_fp 
                        translation_score[token][1] += len(translation_align_tokens)
                        # translation_tp_fn 
                        translation_score[token][2] += len(ref_align_tokens)
                     
        translation_tp = 0
        translation_tp_fp = 0
        translation_tp_fn = 0
      
        for token in translation_score:
            translation_tp +=  translation_score[token][0]               
            translation_tp_fp +=  translation_score[token][1]               
            translation_tp_fn +=  translation_score[token][2]               
    
        translation_precisions.append(translation_tp * 1.0 / translation_tp_fp)   
        translation_recalls.append(translation_tp * 1.0 / translation_tp_fn)
        translation_f1s.append((2.0 * translation_precisions[-1] * translation_recalls[-1] / (translation_precisions[-1] + translation_recalls[-1])))
    prettyPrint(translation_f1s, translation_precisions, translation_recalls)

def getAllWordList(dict_path):
    tgt_dict_lines = codecs.open(dict_path, 'r', 'UTF-8').readlines()
    words = []
    for line in tgt_dict_lines[:]:
        word = line.split()[0]
        word = word.lower()
        words.append(word)
    return words

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-ra", "--ref_align_path", help="source-reference alignment file path (output of fast_align)",type=str)
    parser.add_argument("-ta", "--translation_align_paths", default=[], nargs='+', help="source-translation alignment files path (output of fast_align)")
    parser.add_argument("-s", "--src_path", help="source of test file",type=str)
    parser.add_argument("-r", "--ref_path", help="reference of test file",type=str)
    parser.add_argument('-t', '--trans_paths', default=[], nargs='+', help="a list of translation of test file from different systems")
    parser.add_argument("-w", "--word_list_path", help="path to a list of words to evaluate on",type=str)
    args = parser.parse_args()  
    ref_align_path = args.ref_align_path
    translation_align_paths = args.translation_align_paths
    src_path = args.src_path
    ref_path = args.ref_path
    translation_paths = args.trans_paths
    word_list_path = args.word_list_path

    word_list = getAllWordList(word_list_path)


    calculateScore(ref_align_path, translation_align_paths, src_path, ref_path, translation_paths, word_list)

if __name__ == '__main__':
  main()  

