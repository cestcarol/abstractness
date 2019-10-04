'''
Extract from wikipedia titles concept words (end with -ism,-ness) 
and abstract words (randomly chosen in not[concept])
Titles are preprocessed : lowercase, remove stop_words, only alphabetical words
'''

import json
import re
import argparse
from wiki_dump_reader import Cleaner, iterate
from stop_words import get_stop_words
from collections import Counter
from os.path import exists


RE_ALPHABETIC = re.compile('[a-zA-Z]*')
STOP_WORD = get_stop_words('en') + ['']
OUTFILE = './data/'


def clean_title(title):
    abstracts = []
    concrets = []
    title = re.findall(RE_ALPHABETIC, title.lower())
    
    for w in title:
        if len(w) > 2 and w not in STOP_WORD:
            if w.endswith('ism') or w.endswith('ness'):
                abstracts.append(w)
            else:
                concrets.append(w)
    
    return abstracts, concrets


def write_list(liste, outfile):
    with open(outfile, 'w') as of:
        for item,_ in liste:
            of.write('{}\n'.format(item))

def process_titles(wiki_dump_path, max_art, n_concept=1040):
    n_art = 1
    abstracts = Counter()
    concrets = Counter()
    
    for title, _ in iterate(wiki_dump_path):
        if n_art >= max_art:
            break
        else:
            pos, neg = clean_title(title)
            abstracts.update(pos)
            concrets.update(neg)
        if n_art % 30000 == 0:
            print("{:.2f}% fichiers traités.".format(100*n_art/max_art))
        n_art += 1
    
    write_list(abstracts.most_common(n_concept), OUTFILE+'abstracts')
    write_list(concrets.most_common(n_concept), OUTFILE+'concrets')

def main():
    datapath = './data/enwiki-20170501-pages-articles-multistream(1).xml'

    parser = argparse.ArgumentParser(
        description = 'Extract concepts words (abstract and concrete) from wiki corpus')
    parser.add_argument('wikidump',
                        help="The wikipedia dump")
    args = parser.parse_args()
    datapath = args.wikidump
    
    if exists(datapath):
        process_titles(datapath,6000000)
    else:
        print("Le fichier {} n'existe pas".format(datapath))
    

if __name__ == "__main__":
    main()
