from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, DateField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
from wotd.models import User, PartOfSpeech, Content


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password' , validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken.  Please choose a different name.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken.  Please choose a different name.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password'
                             , validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account for that email.  Please register first.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password' , validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')


class AdminAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    isAdmin = BooleanField('Is Admin', validators=[Optional()])
    submit = SubmitField('Update Account')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update Account')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken.  Please choose a different name.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken.  Please choose a different name.')


class WordForm(FlaskForm):
    word = StringField('Word', validators=[DataRequired()])
    part_o_speech = SelectField('Part of Speech', coerce=int)#, validators=[DataRequired()])
    definition = TextAreaField('Definition', validators=[DataRequired()])
    exampleSentence = TextAreaField('Example Sentence', validators=[DataRequired()])
    ipa = StringField('Pronunciation', validators=[DataRequired()])
    date_published = DateField('Publish Date', validators=[Optional(strip_whitespace=True)])
    submit = SubmitField('Submit')

    def get_parts_of_speech(self):
        self.part_o_speech.choices = [(-1, 'Select...')] + [(p.id, p.partOfSpeech) for p in PartOfSpeech.query.order_by('id')]


class SearchForm(FlaskForm):
    search_data = StringField('Search')
    submit = SubmitField('Search')


class FileForm(FlaskForm):
    file = FileField('Upload Words', validators=[FileAllowed(['txt'])])
    submit = SubmitField('Upload')


class ContentForm(FlaskForm):
    private_title = StringField('Admin Title', validators=[DataRequired()])
    title = StringField('Public Title', validators=[DataRequired()])
    content = TextAreaField('Content Text', validators=[DataRequired()])
    isActive = BooleanField('Is displayed status')
    submit = SubmitField('Upsert')


'''
#May come back for this at a later date
class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')
'''
