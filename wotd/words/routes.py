import random
from datetime import datetime
from sqlalchemy import and_, or_
from flask import render_template, url_for, flash, redirect, request, abort
from wotd import db
from wotd.models import User, Word
from flask_login import current_user, login_required
from wotd.words.forms import WordForm
from wotd.main.forms import SearchForm
from flask import Blueprint


words = Blueprint('words', __name__)


@words.route("/word_bank", methods=['GET', 'POST'])
def word_bank():
    form = SearchForm()
    if form.validate_on_submit and form.search_data.data is not None:
        return redirect(url_for('words.word_bank_search', search_term=form.search_data.data))
    else:
        today = datetime.date(datetime.now())
        page = request.args.get('page', 1, type=int)
        words = Word.query\
            .filter(and_(Word.date_published is not None, Word.date_published <= today))\
            .order_by(Word.date_published.desc())\
            .paginate(per_page=7, page=page)
        num = str(words.total)
    return render_template('word_bank.html', title='Word Bank', words=words, form=form, words_number=num)


@words.route("/word_bank/search/<string:search_term>", methods=['GET', 'POST'])
def word_bank_search(search_term):
    form = SearchForm()
    if form.validate_on_submit and form.search_data.data is not None:
        return redirect(url_for('words.word_bank_search', search_term=form.search_data.data))
    else:
        today = datetime.date(datetime.now())
        search_term = '%' + search_term.lower() + '%'
        page = request.args.get('page', 1, type=int)
        words = Word.query\
                    .filter(
                        and_(
                            Word.date_published is not None, Word.date_published <= today, or_(
                                (Word.word.ilike(search_term))
                                , (Word.definition.ilike(search_term))
                                , (Word.exampleSentence.ilike(search_term))
                            )
                        )
                    )\
            .order_by(Word.date_published.desc())\
            .paginate(per_page=7, page=page)
        num = str(words.total)
    return render_template('word_bank.html', words=words, form=form, words_number=num)


@words.route("/word/random")
def word_random():
    max = Word.query.count()
    rand_int = random.randint(1, max + 1)
    word = Word.query.filter(
        and_(
            Word.id > rand_int
            , Word.date_published != None
        )
    ).first()
    if word is None:
        return redirect(url_for('words.word_random'))
    return redirect(url_for('words.word', word_id=word.id))


@words.route("/word_bank/user/<int:user_id>")
def word_bank_user(user_id):
    form = SearchForm()
    if form.validate_on_submit and form.search_data.data is not None:
        return redirect(url_for('words.word_bank_search', search_term=form.search_data.data))
    else:
        page = request.args.get('page', 1, type=int)
        today = datetime.date(datetime.now())
        words = Word.query.filter(
            and_(
                Word.user_id == user_id
                , or_(
                    Word.date_published != None
                    , Word.date_published > today
                )
            )
        ).order_by(Word.word).paginate(per_page=7, page=page)
        num = str(words.total)
    return render_template('word_bank.html', words=words, form=form, words_number=num)



@words.route("/word/<int:word_id>")
def word(word_id):
    word = Word.query.get_or_404(word_id)
    return render_template('word.html', title=word.word, word=word, user=current_user)


@words.route("/word/new", methods=['GET', 'POST'])
def new_word():
    form = WordForm()
    form.get_parts_of_speech()
    if form.validate_on_submit():
        if form.part_o_speech.data == -1:
            flash('Please choose a part of speech.', 'fail')
        else:
            dupe = Word.query.filter(Word.word == form.word.data
                                     and Word.partOfSpeech_id == form.part_o_speech.data).first()
            if dupe:
                if dupe.date_published:
                    flash('This word was added on {}, you cretin.'.format(dupe.date_published.strftime("%Y-%m-%d")), 'fail')
                else:
                    flash('This word was added on {}, but is unpublished.'.format(dupe.date_added.strftime("%Y-%m-%d")), 'fail')
            else:
                if current_user.is_authenticated:
                    user = current_user
                else:
                    user = User.query.filter(User.id == 0).first()
                word = Word(word=form.word.data
                            , partOfSpeech_id=form.part_o_speech.data
                            , definition=form.definition.data
                            , exampleSentence=form.exampleSentence.data
                            , ipa=form.ipa.data
                            , date_published=form.date_published.data
                            , contributor=user)
                db.session.add(word)
                db.session.commit()
                if current_user.is_authenticated and current_user.isAdmin:
                    flash('Word added, you sot.', 'success')
                else:
                    flash('Word added, awaiting review and scheduling by a site admins, who is slow...', 'success')
                return redirect(url_for('main.home'))
    return render_template('word_upsert.html'
                           , title='Add Word'
                           , form=form
                           , legend='Add word'
                           , user=current_user)


@words.route("/word/<int:word_id>/update", methods=['GET', 'POST'])
@login_required
def update_word(word_id):
    word = Word.query.get_or_404(word_id)
    if word.contributor != current_user and current_user.isAdmin is False:
        abort(403)
    form = WordForm()
    form.get_parts_of_speech()
    if form.validate_on_submit():
        if form.part_o_speech.data == -1:
            flash('Please choose part of speech', 'fail')
        else:
            dupe = Word.query.filter(Word.id != word.id
                                     , Word.word == form.word.data
                                     , Word.partOfSpeech_id == form.part_o_speech.data).first()
            if dupe:
                flash('This word ({}) was added on {}, you cretin.'
                      .format(dupe.id, dupe.date_published.strftime("%Y-%m-%d"))
                      , 'fail')
            else:
                word.word = form.word.data
                word.partOfSpeech_id = form.part_o_speech.data
                word.definition = form.definition.data
                word.exampleSentence = form.exampleSentence.data
                word.ipa = form.ipa.data
                word.date_published = form.date_published.data
                db.session.commit()
                flash('Word updated, you miscreant.', 'success')
                return redirect(url_for('words.word', word_id=word.id))
    elif form.is_submitted() and form.validate() is False:
        flash('This form failed', 'success')
    elif request.method == 'GET':
        form.word.data = word.word
        form.part_o_speech.data = word.partOfSpeech_id
        form.definition.data = word.definition
        form.exampleSentence.data = word.exampleSentence
        form.ipa.data = word.ipa
        form.date_published.data = word.date_published
    return render_template('word_upsert.html'
                           , title='Update ' + word.word
                           , form=form
                           , legend='Update Word'
                           , user=current_user)


@words.route("/word/<int:word_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_word(word_id):
    word = Word.query.get_or_404(word_id)
    if word.contributor != current_user and current_user.isAdmin is False:
        abort(403)
    db.session.delete(word)
    db.session.commit()
    flash('Your word has been deleted, the poor thing.', 'success')
    return redirect(url_for('main.home'))
