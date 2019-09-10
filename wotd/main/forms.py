from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField


class SearchForm(FlaskForm):
    search_data = StringField('Search')
    submit = SubmitField('Search')
