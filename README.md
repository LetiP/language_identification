# Python-Flask Web Application for Language Identification

To see the live website, please go to [http://lident.blebli.de/](http://lident.blebli.de/).

This is a Web App for language identification that without further configuration, will run locally when calling <code>runserver.py</code>. Then open a browser and go to http://localhost:4242/ .

Please be sure you have all Python 3 packages installed from <code>requirements.txt</code>.

The backend for language identification of the input text ist based on the mutual information approach. The only "literature" used for inspiration are the following lines from the [Wikipedia article on the subject](https://en.wikipedia.org/wiki/Language_identification): *One technique is to compare the compressibility of the text to the compressibility of texts in a set of known languages. This approach is known as mutual information based distance measure.*

Basically, we compute the PMI (pointwise mutual information) as a distance measure of independence between two variables: the word (*w*) and the language (*l*) like:

PMI(w, l) = log[ p(w, l)/p(w)/p(l) ]

- p(w) is the probability to find the word *w* in the whole corpus.
- p(l) is the probability to find the language *l* in the corpus.
- p(w, l) is the probability to find the word in the specific language.

PMI=0 if w, l are indepentent, so if the word does not belong to the language. For selecting the language a sentence belongs to, we sum over the PMIs of all words and take the language with the maximum PMI.

The training of the algorithm is based on the sentences corpus from [http://downloads.tatoeba.org/exports/sentences.tar.bz2](http://downloads.tatoeba.org/exports/sentences.tar.bz2). In order to make the corpus smaller, there were selected only 9 of the 200 languages available in the corpus (see the table at the end for details) and only 1,5 millions sentences of these languages.

The code was parallelised on all cores for computation time speedup. Furthermore, the corpus is cached on the disk of the computer in an efficient data structure after the first run. So loading it takes longer only on the first run ever on a machine.

# Evaluation:
Take a random sample of 492 sentences that where **not** used in training and computed the accuracy:
Overall 97,97% accuracy.


| Language | Corpus size | Test size | Accuracy |
| -------- | :---------: | :-------: | -------: |
| English  | 138450      | 132       | 100%     |
| Turkish  | 91051       | 85        | 97,6%    |
| Italian  | 88405       | 97        | 90,7%    |
| German   | 60785       | 60        | 100%     |
| French   | 51078       | 53        | 100%     |
| Spanish  | 41570       | 43        | 100%     |
| Polish   | 13570       | 14        | 100%     |
| Swedish  | 4747        | 5         | 100%     |
| Romanian | 2351        | 3         | 100%     |

For Turkish we have two sentences mistaken for English. This is because the sentences are too short and contain English names:
*Nerelisin?*
and
*Tom ve Mary yoktu.*
The drop in accuracy for Italian is because Italian is mistaken for Spanish, since the two languages are very similar.
