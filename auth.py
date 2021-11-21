from website import DB_NAME
from flask import Blueprint, render_template , request , flash, redirect , url_for
from flask.helpers import flash
from .models import User
from werkzeug.security import generate_password_hash , check_password_hash
from . import db
from flask_login import login_user , login_required , logout_user , current_user

auth = Blueprint('auth' , __name__)

@auth.route('/login', methods= ['GET' , 'POST'] )
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('psw')

        user = User.query.filter_by(email = email).first()
        if user :
            if check_password_hash(user.password , password) :
                flash('log in success' , category='success')
                login_user(user , remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password ' , category='error')

        else : 
            flash('Email does not exist' , category='error')

    return render_template("login.html" , user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up' , methods= ['GET' , 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        pass1 = request.form.get('psw')
        pass2 = request.form.get('psw-repeat')

        user = User.query.filter_by(email = email).first()
        if user :
            flash('Email is already exist' , category='error')
        elif len(pass1) < 8:
            flash ('password must be greater than 8 charachters.' , category='error')

        else:
            new_user = User(email=email , password = generate_password_hash(pass1 , method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash('acount created', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html" , user=current_user)
