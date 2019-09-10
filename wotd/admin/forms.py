from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired


class FileForm(FlaskForm):
    file = FileField('Upload words', validators=[FileAllowed(['txt'])])
    submit = SubmitField('Upload')


class ContentForm(FlaskForm):
    private_title = StringField('admins Title', validators=[DataRequired()])
    title = StringField('Public Title', validators=[DataRequired()])
    content = TextAreaField('Content Text', validators=[DataRequired()])
    isActive = BooleanField('Is displayed status')
    submit = SubmitField('Upsert')


