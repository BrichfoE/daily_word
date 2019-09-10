from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, DateField, SelectField
from wtforms.validators import DataRequired, Optional
from wotd.models import PartOfSpeech


class WordForm(FlaskForm):
    word = StringField('Word', validators=[DataRequired()])
    part_o_speech = SelectField('Part of Speech', coerce=int)
    definition = TextAreaField('Definition', validators=[DataRequired()])
    exampleSentence = TextAreaField('Example Sentence', validators=[DataRequired()])
    ipa = StringField('Pronunciation', validators=[DataRequired()])
    date_published = DateField('Publish Date', validators=[Optional(strip_whitespace=True)])
    submit = SubmitField('Submit')

    def get_parts_of_speech(self):
        self.part_o_speech.choices = [(-1, 'Select...')] \
                                     + [(p.id, p.partOfSpeech) for p in PartOfSpeech.query.order_by('id')]
