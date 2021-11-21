import re
import textract

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from .dataset import df

import seaborn as sns
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

stop_words = set(stopwords.words('english'))
stemmer = SnowballStemmer('english')

class ExtractKeyWords:

    def __init__(self):
        pass

    def run(self):


        # removing such duplicate points
        data = df.drop_duplicates('Job Description')
        
        #containing the number of keywords for each job
        keyes= self.getKeysArray(data)
        """
        ax=sns.countplot(keyes)
        plt.title("Number of keywords in the Description")
        plt.xlabel("Number of keywords")
        plt.ylabel("Number of Description")
        plt.show()
        """

        freq_df = data.asfreq['Keywords']
        print(freq_df)
        #sorted_df.head(-1).plot(kind='bar',figsize=(7,2),legend=False)
        #i=np.arange(20)
      #  plt.title('Frequency of all keywords')
       # plt.xlabel('Keywords')
        #plt.ylabel('Counts')
        #plt.show()


    # function to remove html tags
    def striphtml(self,data):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', str(data))
        return cleantext

    # function to pre-process the text
    def text_preprocess(self,syn_text):
        syn_processed = self.striphtml(syn_text.encode('utf-8')) # html tags removed
        syn_processed=re.sub(r'[^A-Za-z]+',' ',syn_processed) # removing special characters
        words=word_tokenize(str(syn_processed.lower())) # device into words and convert into lower

        #Removing stopwords and joining into sentence   
        syn_processed=' '.join(str(stemmer.stem(j)) for j in words if j not in stop_words and len(j)!=1) 
        return syn_processed

    def getKeysArray(self , data):
        
        keyesArray = []
        jopTitleDAta = data["Job Title"]
        keyWordsData = data["Keywords"]
        
        for k in range(len(jopTitleDAta)) :
            keys = keyWordsData[k].split(",")
            keyesArray.append(len(keys))
        return keyesArray

    def getNumOfKeyes(self,keyes):
        count =0
        for kArr in keyes:
            for k in kArr:
                count += 1
        return count