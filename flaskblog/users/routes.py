from flask import Blueprint
from flask import  render_template, url_for, flash, redirect , request , current_app
from sqlalchemy.exc import SQLAlchemyError
from flaskblog import  db , bcrypt 
from flaskblog.users.forms import (RegistrationForm, LoginForm ,UpdateAccountForm, 
                             DeleteForm, RequestResetForm, ResetPasswordForm)
from flaskblog.models import User, Post
from flask_login import login_user ,current_user, logout_user, login_required
from flaskblog.users.utils import save_picture, send_reset_email
from urllib.parse import urlparse

users = Blueprint('users', __name__)


@users.route("/register", methods=['GET', 'POST'])
def register(): 
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password =  bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            current_app.logger.exception('Failed to create account for %s', form.email.data)
            flash('Could not create your account due to a server error. Please try again.', 'danger')
            return render_template('register.html', title='Register', form=form)
        flash("Your account has been  created Successfuly !" , 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)

@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            # Fix #16: Validate next_page to prevent open redirect
            if next_page and urlparse(next_page).netloc == '':
                return redirect(next_page)
            return redirect(url_for('main.home'))
        else:
            flash('Login unsuccessful. Please check email and password', 'danger')

    return render_template('login.html', title='Login', form=form)


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route("/account",methods=['GET','POST'])
@login_required
def account(): 
    form = UpdateAccountForm()

    if form.validate_on_submit():
        if form.picture.data:
            try:
                picture_file = save_picture(form.picture.data)
            except OSError:
                current_app.logger.exception('Failed to save profile picture for user %s', current_user.id)
                flash('Could not process the uploaded image. Please try a different file.', 'danger')
                return redirect(url_for('users.account'))
            current_user.image_file = picture_file
        # Fix #11: username update was inside the if block, now outside
        current_user.username = form.username.data
        current_user.email = form.email.data
        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            current_app.logger.exception('Failed to update account for user %s', current_user.id)
            flash('Could not update your account due to a server error. Please try again.', 'danger')
            return redirect(url_for('users.account'))
        flash('Your account has been updated!','success')
        return redirect(url_for('users.account'))
    
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)

    return render_template('account.html', title='Account' , image_file=image_file, form=form)


@users.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    post = Post.query.filter_by(author=user)\
            .order_by(Post.date_posted.desc())\
            .paginate(page=page, per_page=2)
    form =  DeleteForm()
    return render_template('user_posts.html', posts=post, form=form, user=user)



@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        try:
            send_reset_email(user)
        except Exception:
            current_app.logger.exception('Failed to send password reset email to %s', form.email.data)
            flash(
                'Could not send the reset email. '
                'Please check the server email configuration (EMAIL_USER / EMAIL_PASS).',
                'danger'
            )
            return redirect(url_for('users.reset_request'))
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset Password',  form=form)


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        # Fix #7: Correct endpoint name
        return redirect(url_for('users.reset_request'))
    form  = ResetPasswordForm()
    if form.validate_on_submit():
        # Fix #5: Update existing user password instead of creating new user
        hashed_password =  bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            current_app.logger.exception('Failed to reset password for user %s', user.id)
            flash('Could not update your password due to a server error. Please try again.', 'danger')
            return render_template('reset_token.html', title='Reset Password', form=form)
        flash("Your password has been updated! You are now able to log in" , 'success')
        return redirect(url_for('users.login'))
    # Fix #6: Render the correct template
    return render_template('reset_token.html', title='Reset Password',  form=form)
