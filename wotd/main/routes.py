from datetime import datetime
from flask import render_template, url_for, redirect
from wotd.models import Word, Content
from wotd.main.forms import SearchForm
from flask import Blueprint

main = Blueprint('main', __name__)

@main.route("/", methods=['GET', 'POST'])
@main.route("/home", methods=['GET', 'POST'])
def home():
    today = datetime.date(datetime.now())
    form = SearchForm()
    if form.validate_on_submit and form.search_data.data is not None:
        return redirect(url_for('words.word_bank_search', search_term=form.search_data.data))
    elif Word.query.filter(Word.date_published == today).count() > 0:
        word = Word.query.filter(Word.date_published == today).first()
    else:
        word = Word()
        word.date_published = datetime.now().date()
    return render_template('home.html', word=word, form=form)


@main.route("/about")
def about():
    active = Content.query.filter_by(isActive=True).first()
    return render_template('about.html', title='About', content=active)
