import PyPDF2
import textract
import re
import glob , os
import nltk
import time
import itertools

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from .models import Candidate

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


SKILLS_DB = [
    'machine learning',
    'python',
    'c',
    'C++',
    'c#',
    'cpp',
    'css',
    'html',
    'sql'
]

RESERVED_WORDS = [
    'school',
    'college',
    'univers',
    'academy',
    'faculty',
]

class PdfFiles:
    # initialize the PDF reader
    def __init__(self ,path ,business,job, requir , bonus , compId , file):
        self.path = path
        self.business = business
        self.job = job
        self.requir = requir.splitlines()
        self.bonus = bonus
        self.compId = compId
        self.file = file
        self.score = 0     

    # extract the relevant data from the resume ( PDF File )
    def searchInPdf(self):
        
        fileUrl = self.path+'\\'+self.file
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
            #txt = textract.process(fileUrl,method='tesseract', language='eng')

        #tokens = word_tokenize(txt)
        #punctuation = ['(',')',';',':','[',']',',']   
        #stop_words = stopwords.words('english')
        #keywords = [word for word in tokens if not word in stop_words and not word in punctuation]
        #for k in keywords:
        #   if self.requir == k:
        #      occurrences +=1
            
        names = self.extractNames(txt)
        email = self.extractEmail(txt)
        phone = self.extractPhoneNum(txt)
        educationInfo = self.extractEducation(txt)
        skillsInfo = self.extractSkills(txt)

        if names:
            if email:
                #if phone:
                 #   print(phone)
                if educationInfo and self.checkEdu(educationInfo):
                        pass
                if skillsInfo and self.checkSkills(skillsInfo):
                            candi = self.createCandidate(names,email, phone , educationInfo , skillsInfo)
                            return candi
        return False
        #return email
    
    def checkEdu(self , educations):
        for edu in educations:
            if edu in self.requir:
                return True
        return False

    def checkSkills(self, skills):
        for skill in skills:
            if skill in skills:
                return True
        return False
    
    def createCandidate(self ,name, email , phonNum , educ , skills):
        companyid= str(self.compId)
        new_candidate = Candidate(name= "farok" ,candiEmail=email[0] , phoneNum = 50 , data = str(educ) + str(skills) , company_id= companyid)
        if new_candidate:
            print('new candidate created')
            return new_candidate
        return False


    # extract the candidate's name
    def extractNames(slef , txt):
        personNames = []

        for sent in nltk.sent_tokenize(txt):
            for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent))):
                if hasattr(chunk , 'label') and chunk.label() == 'PERSON':
                    personNames.append(
                        ''.join(chunk_leave[0] for chunk_leave in chunk.leaves())
                    )
        return personNames
    # extract the candidate's email
    def extractEmail(self , txt):
        e=re.compile(r'(\b[\w.]+@+[\w.]+.+[\w.]\b)')
        return re.findall(e,txt)

    # extract the candidate's phone number
    def extractPhoneNum(self , txt):
        #p=re.compile(r'(\+?(972|0)(\-)?0?(([23489]{1}\d{7})|[5]{1}\d{8}))')
        p=re.compile(r'[\+\(]?[1-9][0-9.\-\(\)]{8,}[0-9]')
        phone = re.findall(p , txt)

        if phone:
            number = ''.join(phone[0])
            print('the number is : ' + number)
            if txt.find(number) >= 0 and len(number) < 20 :
                return number
            return None


    # exrtract candidate's skills
    def extractSkills(self , txt):
        stopWords = set(nltk.corpus.stopwords.words('english'))
        wordTokens = nltk.tokenize.word_tokenize(txt)

        # remove the stop words
        filteredTokens = [w for w in wordTokens if w not in stopWords]

        # remove the punctuation
        filteredTokens = [w for w in wordTokens if w.isalpha()]

        # generate bigrams and trigrams
        bigrams_trigrams = list (map(''.join, nltk.everygrams(filteredTokens,2,3)))

        # create a set to keep the results in 
        foundSkills = set()

        #search for each token in our skills database 
        for token in filteredTokens:
            if token.lower() in SKILLS_DB:
                foundSkills.add(token)

        # search for each bigram and tigram in our skills database
        for ngram in bigrams_trigrams:
            if ngram.lower() in SKILLS_DB:
                foundSkills.add(ngram)

        return foundSkills

    # extract candidate's education
    def extractEducation(self , txt):
        organizations = []

        # first get all the organization name using nltk
        for sent in nltk.sent_tokenize(txt):
            for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent))):
                if hasattr(chunk , 'label') and chunk.label() == 'ORGANIZATION':
                    organizations.append(''.join(c[0] for c in chunk.leaves()))

        # search for each bigram and trigram for reserved words
        education = set()
        for org in organizations:
            for word in RESERVED_WORDS:
                if org.lower().find(word) >= 0:
                    education.add(org)

        return education


