import os , glob
from pickle import FALSE
import re
from re import search
from sys import path
from typing import Set

from pyresparser.utils import extract_skills
from website.models import User , Candidate
from flask_login import login_required , current_user
from flask import Blueprint, render_template , request , flash, redirect , url_for,jsonify
from . import db
import json

import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from nltk.stem import WordNetLemmatizer
from pyresparser import ResumeParser
import spacy
import en_core_web_sm

views = Blueprint('views' , __name__)

@views.route('/' , methods=['GET' , 'POST'])
@login_required
def home():       

    if request.method == 'POST':
        """
        from .extKeyWords import ExtractKeyWords
        k = ExtractKeyWords()
        k.run()
        """
        path = request.form.get('link')
        if path != '':
            return redirect(url_for('views.details' , link = path))
        else:
            flash('Please enter URL ' , category='error')        

    return render_template("home.html" , user=current_user)


@views.route('/details' , methods=['GET' , 'POST'])
@login_required
def details():

    if request.method == 'POST':

        nlp = spacy.load("en_core_web_sm")
        
        path = request.args['link']
        
        business = request.form.get('business')
        jobTitle = request.form.get('job-title')
        desc = request.form.get('description')
        req = request.form.get('requirements')
        bonus = request.form.get('bonus')
        keywords = request.form.get('keywords')
        r = req.splitlines()
        b =bonus.splitlines()
        rb=r+b
        rb.append(jobTitle)
        rb=', '.join(rb)
        text = text_preprocess(rb)
        files = listAllFiles(path)
        f=0 
        while f < len(files):
            fileUrl = path+'\\'+ files[f]
            data = ResumeParser(fileUrl).get_extracted_data() 
            candi=createNewCandi(data , fileUrl)
            c = Candidate.query.filter_by(candiEmail = candi.candiEmail).first()
            if c:
                f+=1
                continue
            else:
                rank =rankCandi(candi , text ,keywords )
                db.session.add(candi)
                print("candid added")
                
            f+=1
        db.session.commit()
        return render_template("candidates.html" , user=current_user )
    

    return render_template("details.html" , user=current_user)
        
@views.route('/candidates' , methods=['GET' , 'POST'])
@login_required
def candidates():

    return render_template("candidates.html" , user=current_user)


@views.route('/delete-candi' , methods=['POST'])
def delete_cadi():
    data = json.load(request.data)
    candiId = data['candiId']
    candi = Candidate.query.get(candiId)

    if candi:
        if candi.company_id == current_user.id:
            db.session.delete(candi)
            db.session.commit()
    return jsonify({})

# list all the files in the same folder
def listAllFiles(path):
    files = []
    os.chdir(path)
    for file in glob.glob('*.pdf'):
        files.append(file)
    for file in glob.glob('*.doc'):
        files.append(file)

    return files

#create a new candidate
def createNewCandi(data , fileUrl):

    candi = Candidate(
        name = data['name'],
        candiEmail = data['email'],
        phoneNum = data['mobile_number'],
        skills = str(data['skills']),
        collageName = data['college_name'],
        degree = str(data['degree']),
        experience = str(data['experience']),
        designation = str(data['designation']), 
        companyNames = str(data['company_names']),
        numOfPages = data['no_of_pages'],
        totalExp = data['total_experience'],
        company_id = current_user.id,
        linkToCV = fileUrl
    )
    return candi

def rankCandi(candi ,text ,keywords):
    
    rank = 0
    numofskill = 0
    if(keywords != ''):
        for skill in candi.skills:
            if skill in keywords:
                numofskill+=1
    else:    
        if candi.experience != None:
            for exp in candi.experience:
                if exp in keywords:
                    rank +=5    

        for skill in candi.skills:
            if skill in text:
                numofskill+=1
                

        if candi.experience != None:
            for exp in candi.experience:
                if exp in text:
                    rank +=5
    if candi.totalExp >1:
        rank+=2
    pages =candi.numOfPages
    while pages > 1:
        rank -= 1
        pages -=1

    rank += int(numofskill/len(text) * 100)

    while rank > 100:
        rank = rank+900
        rank = rank//10
        

    candi.rank = rank
    if numofskill == 0 :
            candi.isMatch = False
    else:
        candi.isMatch = True
    return rank

def text_preprocess(text):

    stop_words = set(stopwords.words('english'))
    stemmer = SnowballStemmer('english')
    syn_processed=re.sub(r"[^a-zA-Z0-9]","",text) # removing special characters
    words=word_tokenize(str(syn_processed.lower())) # device into words and convert into lower

    #Removing stopwords and joining into sentence
    syn_processed=' '.join(str(stemmer.stem(j)) for j in words if j not in stop_words and len(j)!=1) 
    
    return syn_processed