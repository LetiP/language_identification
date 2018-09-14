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


class PMIClassifier(object):
    def __init__(self, dummy_cache=0):
        self.corpus, self.test_data, self.lang_priors = _load_data()

    def mutual_info(self, word, word_prior, lang):
        """ Compute the pointwise mutual information (PMI) for a word to the given language."""
        spec = self.corpus['lang'] == lang
        n = spec.shape[0]
        m = self.lang_priors[lang]
        if n > 0:
            # compute the joint probabiblity for word and language
            joint = self.corpus[spec]['sentence'].str.count(
                word).sum() / spec.shape[0]
        else:
            return 0

        if joint > 0:
            return np.log(joint / (word_prior * m))
        else:
            return 0

    def word_ident(self, words):
        """ Determine the language identity of each word by taking the maximum PMI."""
        word_res = {}
        for word in words:
            N = self.corpus.shape[0]
            # compute the prior probability for the specific word
            word_prior = self.corpus['sentence'].str.count(word).sum() / N

            res = {}
            for lang, _ in self.lang_priors.iteritems():
                res[lang] = self.mutual_info(word, word_prior, lang)
            found = max(res, key=res.get)

            word_res = sum_to_dict(word_res, found, res[found])

        return word_res

    def identify(self, sentence):
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
                    jobs.append(executor.submit(self.word_ident, words))
            # merge the results from every core
            for job in concurrent.futures.as_completed(jobs):
                word_res = job.result()
                for key in word_res:
                    test_res = sum_to_dict(test_res, key, word_res[key])

        return max(test_res, key=test_res.get)

    def test(self):
        """ Measure the accuracy of the method. """
        print('test shape is', self.test_data.shape[0])
        right = 0
        right_per_lang = {}
        print(self.test_data['lang'].value_counts())
        print(self.corpus['lang'].value_counts())
        for _, row in self.test_data.iterrows():
            lang = row['lang']
            sentence = row['sentence']
            found = self.identify(sentence.strip('?!,.').split(' '))
            print('Predicted:', found, '   Ground truth:', lang, sentence)
            if found == lang:
                right += 1
                right_per_lang = sum_to_dict(right_per_lang, lang, 1)

        print('Accuracy is', right/self.test_data.shape[0])
        print(right_per_lang)

@MEMORY.cache(verbose=True)
def _load_data(dummy_cache=0):
    """ Load the corpus into memory. Cached when calling it the second time on the same computer.
    The 'dummy_cache' variable stays only for the purpose of caching when there is the same function parameter.
    Does not work with no parameters.
    Needs to be outside of the class, for chaching the computationally expensive part."""

    # smallify_corpus()

    corpus = pd.read_csv(make_path('small_corpus.csv'))[
        ['lang', 'sentence']]
    test_data = pd.read_csv(make_path('test_data.csv'))[
        ['lang', 'sentence']]

    def language_priors(corpus):
        """ Precompute the priors for the language. Same for every word."""
        return corpus['lang'].value_counts(normalize=True)

    lang_priors = language_priors(corpus)

    return corpus, test_data, lang_priors

def make_path(filename):
    ''' Build the correct path for app or running from main. '''
    if __name__ == "__main__":
        path = path_join(sys.path[0], filename)
    else:
        path = path_join(sys.path[0], 'lang_ident', filename)

    return path


def smallify_corpus():
    ''' Take only 9 languages and 1/6 of all sentences. '''
    path = make_path('sentences.csv')
    corpus = pd.read_csv(path, sep='\t', names=[
        'idx', 'lang', 'sentence'])[['lang', 'sentence']]

    # make the dataset smaller my restricting languages
    corpus = corpus[corpus['lang'].isin(
        ['deu', 'eng', 'ron', 'swe', 'fra', 'tur', 'ita', 'spa', 'pol'])]

    # make dataset smaller by taking only 1/4th of it
    drop_indices = np.random.choice(
        corpus.index, corpus.shape[0]//7*6, replace=False)
    test_indices = np.random.choice(
        drop_indices, len(drop_indices)//6000, replace=False)
    test_data = corpus.loc[test_indices]
    corpus = corpus.drop(drop_indices)

    corpus.to_csv(make_path('small_corpus.csv'))
    test_data.to_csv(make_path('test_data.csv'))


def sum_to_dict(d, key, value):
    """ Helper function to sum value of existing keys in dict. """
    if key not in d:
        d[key] = value
    else:
        d[key] += value
    return d


CLASSIFIER = PMIClassifier(0)  # argument zero is for caching with joblib


if __name__ == "__main__":
    # smallify_corpus()
    CLASSIFIER.test()
