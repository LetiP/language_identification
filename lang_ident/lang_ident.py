import pandas as pd
from collections import Counter
import numpy as np
import concurrent.futures
from joblib import Memory
from os.path import expanduser, join as path_join, isfile
from subprocess import call
import sys

import time

CACHE_PATH = expanduser("~/.python_cache")
call("mkdir -p {}".format(CACHE_PATH), shell=True)
MEMORY = Memory(cachedir=CACHE_PATH)


@MEMORY.cache(verbose=True)
def load_corpus(dummy_cache=0):
    """ Load the corpus into memory. Cached when calling it the second time on the same computer.
    The 'dummy_cache' variable stays only for the purpose of caching when there is the same function parameter.
    Does not work with no parameters. """
    path = path_join(sys.path[0], 'lang_ident', 'sentences.csv')
    corpus = pd.read_csv(path, sep='\t', names=[
        'idx', 'lang', 'sentence'])[['lang', 'sentence']]

    # make the dataset smaller my restricting languages
    corpus = corpus[corpus['lang'].isin(
        ['deu', 'eng', 'ron', 'swe', 'fra', 'tur', 'rus', 'ita', 'spa', 'pol'])]

    # make dataset smaller by taking only 1/4th of it
    drop_indices = np.random.choice(corpus.index, corpus.shape[0]//7*6, replace=False)
    corpus = corpus.drop(drop_indices)

    def language_priors(corpus):
        """ Precompute the priors for the language. Same for every word."""
        return corpus['lang'].value_counts(normalize=True)

    lang_priors = language_priors(corpus)

    return corpus, lang_priors


CORPUS, LANG_PRIORS = load_corpus()

def sum_to_dict(d, key, value):
    """ Helper function to sum value of existing keys in dict. """
    if key not in d:
        d[key] = value
    else:
        d[key] += value
    return d


def mutual_info(word, word_prior, lang, lang_priors=LANG_PRIORS, corpus=CORPUS):
    """ Compute the pointwise mutual information (PMI) for a word to the given language."""
    spec = corpus['lang'] == lang
    n = spec.shape[0]
    m = lang_priors[lang]
    if n > 0:
        # compute the joint probabiblity for word and language
        joint = corpus[spec]['sentence'].str.count(word).sum() / spec.shape[0]
    else:
        return 0

    if joint > 0:
        return np.log(joint / (word_prior * m))
    else:
        return 0


def word_ident(words, lang_priors=LANG_PRIORS, corpus=CORPUS):
    """ Determine the language identity of each word by taking the maximum PMI."""
    word_res = {}
    for word in words:
        N = corpus.shape[0]
        # compute the prior probability for the specific word
        word_prior = corpus['sentence'].str.count(word).sum() / N

        res = {}
        for lang, _ in lang_priors.iteritems():
            res[lang] = mutual_info(
                word, word_prior, lang, lang_priors, corpus)
        found = max(res, key=res.get)

        word_res = sum_to_dict(word_res, found, res[found])

    found = max(word_res, key=word_res.get)

    return found, word_res[found]


def identify(sentence, lang_priors=LANG_PRIORS, corpus=CORPUS):
    """ Determine the language identity for the whole sentence. Parallelized."""
    n_worker = 4
    test_res = {}
    n = len(sentence) // n_worker
    ExecutorType = concurrent.futures.ProcessPoolExecutor
    with ExecutorType(max_workers=n_worker) as executor:
        jobs = []
        for i in range(n_worker):
            # split up the sentence in n_worker lists to parallelize computation on cores
            if i < n_worker - 1:
                words = sentence[i * n:(i + 1) * n]
            else:
                words = sentence[i * n:]
            if len(words) > 0:
                jobs.append(executor.submit(
                    word_ident, words, lang_priors, corpus))
        # merge the results from every core
        for job in concurrent.futures.as_completed(jobs):
            key, value = job.result()
            test_res = sum_to_dict(test_res, key, value)

    return max(test_res, key=test_res.get)
