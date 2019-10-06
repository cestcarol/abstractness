# Learning Concept Abstractness

Reproduction of experience of the paper 'Learning Concept Abstracness using weak supervision' from Rabinovich et al. (EMNLP, 2018). Using two suffixes ('-ism', '-ness') known to represent rather abstract words than concretes, a list is extracted from english wikipedia titles. From the wikipedia articles is then extracted 500 sentences for each word in the list. 

## How to run the scripts from wikipedia dump
Order : 
1. extract_words.py 
1. extract_sentences.py

### extract_words
`python extract_words path_to_wiki_dump`
Read the titles from wiki_dump. Remove stop words. Words ending with -ness and -ism are added to data/abstracts and others to data/concrets. 
Only 1040 most common ones are stored on files.

### extract_sentences
`python extract_sentences path_to_wiki_dump`
Read the articles from wiki_dump. 
Extract for each words of data/abstracts and data/concrets 500 sentences containing them.
Write the output as json file in data/concrete_sent.json and data/abstract_sent.json
