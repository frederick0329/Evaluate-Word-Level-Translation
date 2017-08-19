# evaluate_word_translation

This repo contains code for calcualting word level transaltion performace for machine translation.

The translation performance is based on f1, precision, and recall.

The code is used for the paper Handling Homographs in Neural Machine Translation.

## Before running 

You will need the following file prepared before running.

* source of test file
* reference of test file
* translation of the model
* alignment of the source file and the reference file (output of fast\_align)
* alignment of the source file and the translation file (ouput of fast\_align)
* list of words to evaluate on 

For the paper, we concantenate the training data with the reference and translations of the two systems to produce the alignments. 
Details of running fast\_align can be found [here](https://github.com/clab/fast_align)

## Requirements
* python 3

## Usage 
```
python evaluate.py -ra src-ref.align -ta src-translation1.align -s src.txt -r ref.txt -t translation1.txt -w homograph_list.txt
```
For the all words results of the paper, we extract the 50000 tokens from our English dictionary for our neural model filtering out non-english words as our word list.

