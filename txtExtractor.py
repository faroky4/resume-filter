import os
import re
import nltk
import constants as cs
import pandas as pd

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFSyntaxError

class Extractor:
    
    def __init__(self , path ,file , extension):
        self.path = path 
        self.file = file
        self.extension = extension

    def extract_skills(nlp_text, noun_chunks, skills_file=None):
    
        tokens = [token.text for token in nlp_text if not token.is_stop]
        if not skills_file:
            data = pd.read_csv(
                os.path.join(os.path.dirname(__file__), 'skills.csv')
            )
        else:
            data = pd.read_csv(skills_file)
        skills = list(data.columns.values)
        skillset = []
        # check for one-grams
        for token in tokens:
            if token.lower() in skills:
                skillset.append(token)

        # check for bi-grams and tri-grams
        for token in noun_chunks:
            token = token.text.lower().strip()
            if token in skills:
                skillset.append(token)
        return [i.capitalize() for i in set([i.lower() for i in skillset])]


    def cleanup(token, lower=True):
        if lower:
            token = token.lower()
        return token.strip()

    def extract_education(nlp_text):
   
        edu = {}
        # Extract education degree
        try:
            for index, text in enumerate(nlp_text):
                for tex in text.split():
                    tex = re.sub(r'[?|$|.|!|,]', r'', tex)
                    if tex.upper() in cs.EDUCATION and tex not in cs.STOPWORDS:
                        edu[tex] = text + nlp_text[index + 1]
        except IndexError:
            pass

        # Extract year
        education = []
        for key in edu.keys():
            year = re.search(re.compile(cs.YEAR), edu[key])
            if year:
                education.append((key, ''.join(year.group(0))))
            else:
                education.append(key)
        return education


    def extract_experience(resume_text):

        wordnet_lemmatizer = WordNetLemmatizer()
        stop_words = set(stopwords.words('english'))
    
        # word tokenization
        word_tokens = nltk.word_tokenize(resume_text)
    
        # remove stop words and lemmatize
        filtered_sentence = [
                w for w in word_tokens if w not
                in stop_words and wordnet_lemmatizer.lemmatize(w)
                not in stop_words
            ]
        sent = nltk.pos_tag(filtered_sentence)
    
        # parse regex
        cp = nltk.RegexpParser('P: {<NNP>+}')
        cs = cp.parse(sent)
    
        # for i in cs.subtrees(filter=lambda x: x.label() == 'P'):
        #     print(i)
    
        test = []
    
        for vp in list(
            cs.subtrees(filter=lambda x: x.label() == 'P')
        ):
            test.append(" ".join([
                i[0] for i in vp.leaves()
                if len(vp.leaves()) >= 2])
            )
    
        # Search the word 'experience' in the chunk and
        # then print out the text after it
        x = [
            x[x.lower().index('experience') + 10:]
            for i, x in enumerate(test)
            if x and 'experience' in x.lower()
        ]
        return x