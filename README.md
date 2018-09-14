# Python-Flask Web Wpplication for Language Identification

To see the live website, please go to [http://lident.blebli.de/](http://lident.blebli.de/).

This is a Web App for language identification that will without further configuration, will run locally when calling <code>runserver.py</code>.

Please be sure, you have all Python 3 packages installed from <code>requirements.txt</code>.

The backend for language identification of the input text ist based on the mutual information approach. The only "literature" inspiration for it where the following lines from the [Wikipedia article on the subject](https://en.wikipedia.org/wiki/Language_identification), specifically the following two sentences: *One technique is to compare the compressibility of the text to the compressibility of texts in a set of known languages. This approach is known as mutual information based distance measure.*

The training of the algorithm ist based on the sentences corpus from [http://downloads.tatoeba.org/exports/sentences.tar.bz2](http://downloads.tatoeba.org/exports/sentences.tar.bz2). In order to make the corpus smaller, there where selected only 9 of the 200 languages available in the corpus and only 1,5 millions of sentences of these languages.

The code was parallelised on all cores for computation time speedup. Furthermore, the corpus is cached on the disk of the computer in an efficient data structure after the first run. So loading it takes longer only on the first run ever on a machine.

Evaluation:
Take a random sample of 492 sentences that where **not** used in training and computed the accuracy:
Overall 97,97% accuracy.
