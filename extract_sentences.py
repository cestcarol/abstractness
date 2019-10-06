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
DEFAULT_SENT_PER_CONCEPT = 500
SENT_MIN_SIZE = 9
SENT_MAX_SIZE = 70


def load_concepts():
    with open('./data/abstracts') as f: 
        abstract_words = {i.rstrip('\n') : [] for i in f.readlines()}
    
    with open('./data/concrets') as f:
        concrete_words = {i.rstrip('\n') : [] for i in f.readlines()}
    
    with open('./data/wiki_1500.csv') as f:
        validation_words = [l.lower().split('\t')[0] for l in f.readlines()]
        validation_words_no_stopwords = { s :
                                          ' '.join([token for token in s.split() if token not in STOP_WORD])
                                          for s in validation_words
        }
        validation_words = {i : [] for i in validation_words}
    
    return abstract_words, concrete_words, validation_words, validation_words_no_stopwords


def write_json(data, outfile):
    with open(outfile, 'w') as of:
        of.write(json.dumps(data))    


def dictfull(d):
    for k in d.keys():
        if len(d[k]) < 500:
            return False
    return True


def update_dict(list_tokens, dict, sent_per_concept, mask_key=True):
    updated = False
    for k in dict:
        if len(dict[k]) < sent_per_concept:
            if k in list_tokens:
                s = ' '.join(list_tokens)
                s = s.replace(k,'xxxxxx') if mask_key else s
                dict[k].append(s)
                updated = True
    return updated

def update_dict_ngram(list_tokens, dict, dict_no_stop_word, sent_per_concept, mask_key=True):
    updated = False
    for k in dict:
        if len(dict[k]) < sent_per_concept:
            if dict_no_stop_word[k] in list_tokens:
                s = ' '.join(list_tokens)
                s = s.replace(k,'xxxxxx') if mask_key else s
                dict[k].append(s)
                updated = True
    return updated

def extract_sentences(sentences, abstract_words, concrete_words, validation_words, validation_words_no_stopwords, sent_per_concept):
    for s in sentences:
        list_tokens = re.findall(RE_ALPHABETIC, s.lower())
        list_tokens = [w for w in list_tokens if w not in STOP_WORD]
        s_in_train = False
        if len(list_tokens) > SENT_MIN_SIZE and len(list_tokens) < SENT_MAX_SIZE:
            s_in_train = update_dict(list_tokens, abstract_words, sent_per_concept)
            s_in_train = s_in_train or update_dict(list_tokens, concrete_words, sent_per_concept)
            if not s_in_train:
                update_dict_ngram(list_tokens, validation_words, validation_words_no_stopwords, sent_per_concept, mask_key=False)

def process_text(wiki_dump_path, max_art, sent_per_concept):
    n_art = 1
    abstract_words, concrete_words, validation_words, validation_words_no_stopwords = load_concepts()
    sent_detector = data.load('tokenizers/punkt/english.pickle')
    cleaner = Cleaner()
    
    for _, text in iterate(wiki_dump_path):
        if n_art >= max_art:
            break
        else:
            s = sent_detector.tokenize(cleaner.clean_text(text))
            extract_sentences(s, abstract_words, concrete_words, validation_words, validation_words_no_stopwords, sent_per_concept)
        if n_art % 50000 == 0:
            print("{:.2f}% fichiers traités.".format(100*n_art/max_art))
        n_art += 1

    write_json(abstract_words, DATA_FOLDER+'abstract_sent.json')
    write_json(concrete_words, DATA_FOLDER+'concrete_sent.json')
    write_json(validation_words, DATA_FOLDER+'validation_sent.json')

def main():
    datapath = './data/enwiki-20170501-pages-articles-multistream(1).xml'

    parser = argparse.ArgumentParser(
        description = 'Extract 500 sentences/concept from wiki corpus')
    parser.add_argument('wikidump',
                        help="The wikipedia dump"
    )
    parser.add_argument('-ns',
                        help="The number of sentences per concept to extract"
    )
    args = parser.parse_args()
    datapath = args.wikidump
    sent_per_concept = args.ns if args.ns else DEFAULT_SENT_PER_CONCEPT

    if exists(datapath):
        process_text(datapath, 10000, sent_per_concept)
    else:
        print("Le fichier {} n'existe pas".format(datapath))


if __name__ == "__main__":
    main()
