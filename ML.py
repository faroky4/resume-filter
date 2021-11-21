from glob import glob
import itertools
from os import path
import os.path
import re
import tarfile
import time
import sys
import PyPDF2

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

from urllib.request import urlretrieve
from sklearn.datasets import get_data_home
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.linear_model import Perceptron
from sklearn.naive_bayes import MultinomialNB

from .extractPdfTxt import PdfFiles


class ML:
    def __init__(self , path ,business , job, require ,bonus ):
        self.path = path
        self.business = business
        self.job = job
        self.require = require
        self.bonus = bonus
        self.files = []
        self.data_stream = self.getDatastream()
        
    # Create the vectorizer and limit the number of features to a reasonable
    # maximum
    vectorizer = HashingVectorizer(decode_error='ignore', n_features=2 ** 18,
                                alternate_sign=False)

    def listAllFiles(self):
        os.chdir(self.path)
        for file in glob.glob('*.pdf'):
            self.files.append(file)
            print(file)

    def getDatastream(self):
        #return PdfFiles(self.path,self.business,self.job,self.require,self.bonus)
        f=0
        self.listAllFiles()
        while f < len(self.files):
            
            occurrences = 0
            fileUrl = self.path+'\\'+self.files[f]
            pdfFile = open (fileUrl , 'rb')
            pdfFile = PyPDF2.PdfFileReader(pdfFile)

            NumOfPages = pdfFile.getNumPages()

            txt = ""
            for i in range (0,NumOfPages):
                pageObj = pdfFile.getPage(i)
                txt += pageObj.extractText()
            if txt != "":
                txt=txt
            else:
                pass
                f += 1

    all_classes = np.array([0, 1])
    positive_class = 'acq'

    partial_fit_classifiers = {
        'SGD': SGDClassifier(max_iter=5),
        'Perceptron': Perceptron(),
        'NB Multinomial': MultinomialNB(alpha=0.01),
        'Passive-Aggressive': PassiveAggressiveClassifier(),
    }


    def get_minibatch(self,doc_iter, size, pos_class=positive_class):
   
        data = [('{title}\n\n{body}'.format(**doc), pos_class in doc['topics'])
            for doc in itertools.islice(doc_iter, size)
            if doc['topics']]
        if not len(data):
            return np.asarray([], dtype=int), np.asarray([], dtype=int)
        X_text, y = zip(*data)
        return X_text, np.asarray(y, dtype=int)


    def iter_minibatches(self,doc_iter, minibatch_size):
        """Generator of minibatches."""
        X_text, y = self.get_minibatch(doc_iter, minibatch_size)
        while len(X_text):
            yield X_text, y
            X_text, y = self.get_minibatch(doc_iter, minibatch_size)


    # test data statistics
    test_stats = {'n_test': 0, 'n_test_pos': 0}
    # First we hold out a number of examples to estimate accuracy
    n_test_documents = 1000
    tick = time.time()
    X_test_text, y_test = get_minibatch(data_stream, 1000)
    parsing_time = time.time() - tick
    tick = time.time()
    X_test = vectorizer.transform(X_test_text)
    vectorizing_time = time.time() - tick
    test_stats['n_test'] += len(y_test)
    test_stats['n_test_pos'] += sum(y_test)

    cls_stats = {}

    for cls_name in partial_fit_classifiers:
        stats = {'n_train': 0, 'n_train_pos': 0,
                 'accuracy': 0.0, 'accuracy_history': [(0, 0)], 't0': time.time(),
                 'runtime_history': [(0, 0)], 'total_fit_time': 0.0}
        cls_stats[cls_name] = stats

    get_minibatch(data_stream, n_test_documents)

    # We will feed the classifier with mini-batches of 1000 documents; this means
    # we have at most 1000 docs in memory at any time.  The smaller the document
    # batch, the bigger the relative overhead of the partial fit methods.
    minibatch_size = 1000

    # Create the data_stream that parses Reuters SGML files and iterates on
    # documents as a stream.
    minibatch_iterators = iter_minibatches(data_stream, minibatch_size)
    total_vect_time = 0.0

    def runMl(self):
        # Main loop : iterate on mini-batches of examples
        for i, (X_train_text, y_train) in enumerate(self.minibatch_iterators):

            tick = time.time()
            X_train = self.vectorizer.transform(X_train_text)
            self.total_vect_time += time.time() - tick
            for cls_name, cls in self.partial_fit_classifiers.items():
                tick = time.time()
                # update estimator with examples in the current mini-batch
                cls.partial_fit(self.X_train, self.y_train, classes=self.all_classes)

                # accumulate test accuracy stats
                self.cls_stats[cls_name]['total_fit_time'] += time.time() - tick
                self.cls_stats[cls_name]['n_train'] += self.X_train.shape[0]
                self.cls_stats[cls_name]['n_train_pos'] += sum(self.y_train)
                tick = time.time()
                self.cls_stats[cls_name]['accuracy'] = cls.score(self.X_test, self.y_test)
                self.cls_stats[cls_name]['prediction_time'] = time.time() - tick
                acc_history = (self.cls_stats[cls_name]['accuracy'],
                               self.cls_stats[cls_name]['n_train'])
                self.cls_stats[cls_name]['accuracy_history'].append(acc_history)
                run_history = (self.cls_stats[cls_name]['accuracy'],
                               self.total_vect_time + self.cls_stats[cls_name]['total_fit_time'])
                self.cls_stats[cls_name]['runtime_history'].append(run_history)

                if i % 3 == 0:
                    print(self.progress(cls_name, self.cls_stats[cls_name]))
            if i % 3 == 0:
                print('\n')