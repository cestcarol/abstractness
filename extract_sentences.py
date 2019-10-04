from nltk.tokenize import word_tokenize
from nltk import data
from wiki_dump_reader import Cleaner, iterate
from stop_words import get_stop_words
from os.path import exists
import json
import re
import argparse

RE_ALPHABETIC = re.compile('[a-zA-Z]*')
STOP_WORD = get_stop_words('en') + ['']
DATA_FOLDER = './data/'
SENT_PER_CONCEPT = 500

def load_concepts():
    with open('./data/abstracts') as f: 
        abstract_words = {i.rstrip('\n') : [] for i in f.readlines()}
    
    with open('./data/concrets') as f:
        concrete_words = {i.rstrip('\n') : [] for i in f.readlines()}
    
    with open('./data/wiki_1500.csv') as f:
        validation_words = [l.lower().split('\t')[0] for l in f.readlines()]
        validation_words = {i : [] for i in validation_words}
    
    return abstract_words, concrete_words, validation_words


def write_json(data, outfile):
    with open(outfile, 'w') as of:
        of.write(json.dumps(data))    


def dictfull(d):
    for k in d.keys():
        if len(d[k]) < 500:
            return False
    return True

        
def extract_train_sentences(sentences, abstract_words, concrete_words):
    for s in sentences:
        list_tokens = re.findall(RE_ALPHABETIC, s.lower())
        list_tokens = [w for w in list_tokens if w not in STOP_WORD]
        if len(list_tokens) > 9 and len(list_tokens) < 70:
            for k in abstract_words:
                if len(abstract_words[k]) < SENT_PER_CONCEPT:
                    if k in list_tokens:
                        abstract_words[k].append(' '.join(list_tokens))
            for k in concrete_words:
                if len(concrete_words[k]) < SENT_PER_CONCEPT:
                    if k in list_tokens:
                        concrete_words[k].append(' '.join(list_tokens))



def process_text(wiki_dump_path, max_art):
    n_art = 1
    abstract_words, concrete_words, validation_words = load_concepts()
    sent_detector = data.load('tokenizers/punkt/english.pickle')
    cleaner = Cleaner()
    
    for _, text in iterate(wiki_dump_path):
        if n_art >= max_art or (dictfull(abstract_words) and dictfull(concrete_words)):
            break
        else:
            s = sent_detector.tokenize(cleaner.clean_text(text))
            extract_train_sentences(s, abstract_words, concrete_words)
        if n_art % 50000 == 0:
            print("{:.2f}% fichiers traités.".format(100*n_art/max_art))
        n_art += 1

    write_json(abstract_words, DATA_FOLDER+'abstract_sent.json')
    write_json(concrete_words, DATA_FOLDER+'concrete_sent.json')
#    write_json(validation_words, DATA_FOLDER+'validation_sent')

def main():
    datapath = './data/enwiki-20170501-pages-articles-multistream(1).xml'

    parser = argparse.ArgumentParser(
        description = 'Extract 500 sentences/concept from wiki corpus')
    parser.add_argument('wikidump',
                        help="The wikipedia dump")
    args = parser.parse_args()
    datapath = args.wikidump
    
    if exists(datapath):
        process_text(datapath,6000000)
    else:
        print("Le fichier {} n'existe pas".format(datapath))


if __name__ == "__main__":
    main()
