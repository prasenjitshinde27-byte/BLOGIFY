from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo,ValidationError
from flaskblog.models import User


def validate_unique_username(username, exclude=None):
    if username.data == exclude:
        return
    if User.query.filter_by(username=username.data).first():
        raise ValidationError('That username is taken. Please choose a different one.')


def validate_unique_email(email, exclude=None):
    if email.data == exclude:
        return
    if User.query.filter_by(email=email.data).first():
        raise ValidationError('That email is taken. Please choose a different one.')



class RegistrationForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[DataRequired(), Length(min=2, max=20)]
    )

    email = StringField(
        'Email',
        validators=[DataRequired(), Email()]
    )

    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=8, max=128)]
    )

    confirm_password = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password')]
    )

    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        validate_unique_username(username)

    def validate_email(self, email):
        validate_unique_email(email)



class LoginForm(FlaskForm):
    email = StringField(
        'Email',
        validators=[DataRequired(), Email()]
    )

    password = PasswordField(
        'Password',
        validators=[DataRequired()]
    )

    remember = BooleanField('Remember Me')

    submit = SubmitField('Login')



class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    
    submit = SubmitField('Update')

    def validate_username(self, username):
        validate_unique_username(username, exclude=current_user.username)

    def validate_email(self, email):
        validate_unique_email(email, exclude=current_user.email)
            
    
class DeleteForm(FlaskForm):
    submit = SubmitField('Delete')


class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
            user = User.query.filter_by(email=email.data).first()
            if user is None:
                raise ValidationError('There is no account with that email. You must register first.')


class ResetPasswordForm(FlaskForm):
       password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=8, max=128)] )
    
       confirm_password = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password')])
       submit = SubmitField('Reset Password')