from datetime import datetime
from flask import Blueprint, render_template, flash, redirect, url_for, session
from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash
from app import db
from blog.views import blog
from models import User
from users.forms import RegisterForm, LoginForm
import pyotp


users_blueprint = Blueprint('users', __name__, template_folder='templates')

@users_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user:
            flash('Username address already in use')
            return render_template('register.html', form=form)
        new_user = User(username=form.username.data, password=form.password.data,
                        pinkey=form.pinkey.data)

        db.session.add(new_user)
        db.session.commit()

        #return login()
        session['logins'] = 0
        return redirect(url_for('users.login'))

    return render_template('register.html', form=form)


@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if not session.get('logins'):
        session['logins'] = 0
    elif session.get('logins') >=3:
        flash('Number of incorrect logins exceeded')


    if form.validate_on_submit():

        session['logins'] += 1

        user = User.query.filter_by(username=form.username.data).first()

        if not user or not check_password_hash(user.password, form.password.data):
            flash('Please check your login details and try again')

            if session['logins'] == 3:
                flash('Number of incorrect logins exceeded')
            elif session['logins'] == 2:
                flash('Please check your login details and try again -  1 attempt remaining')
            elif session['logins'] == 1:
                flash('Please check your login details and try again -  2 attempts remaining')


            return render_template('login.html', form=form)

        if pyotp.TOTP(user.pinkey).verify(form.otp.data):
            session['logins'] = 0

            login_user(user)

            user.last_logged_in = user.current_logged_in
            user.current_logged_in = datetime.now()
            db.session.add(user)
            db.session.commit()
        else:
            flash("You have supplied an invalid 2FA token!", "danger")
        return blog()

    return render_template('login.html', form=form)

@users_blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
