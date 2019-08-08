import os
import secrets
import random
from datetime import datetime
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from wotd import app, db, flask_bcrypt
from wotd.forms import RegistrationForm, LoginForm, UpdateAccountForm, WordForm, SearchForm #, PostForm
from wotd.models import User, Word#, Post
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
@app.route("/home")
def home():
    today = datetime.date(datetime.now())
    if Word.query.filter(Word.date_published == today).count() > 0:
        word = Word.query.filter(Word.date_published == today).first()
    else:
        word = Word()
        word.date_published = datetime.now().date()
    return render_template('home.html', word=word)


@app.route("/word_bank", methods=['GET', 'POST'])
def word_bank():
    form = SearchForm()
    if form.validate_on_submit and form.search_data.data is not None:
        return redirect(url_for('word_bank_search', search_term=form.search_data.data))
    else:
        words = Word.query.order_by(Word.date_published.desc()).limit(7)
        num = str(words.count())
    return render_template('word_bank.html', words=words, form=form, words_number=num)


@app.route("/word_bank/search/<string:search_term>", methods=['GET', 'POST'])
def word_bank_search(search_term):
    form = SearchForm()
    if form.validate_on_submit and form.search_data.data is not None:
        return redirect(url_for('word_bank_search', search_term=form.search_data.data))
    all_words = Word.query.all()
    words = [x for x in all_words
                if search_term in x.word
                or search_term in x.definition
                or search_term in x.exampleSentence]
    num = str(len(words))
    return render_template('word_bank.html', words=words, form=form, words_number=num)


@app.route("/word_bank/random")
def word_bank_random():
    form = SearchForm()
    if form.validate_on_submit and form.search_data.data is not None:
        return redirect(url_for('word_bank_search', search_term=form.search_data.data))
    else:
        max = Word.query.count()
        rand_int = random.randint(1, max + 1)
        words = Word.query.filter_by(id=rand_int).all()
        num = '1'
    return render_template('word_bank.html', words=words, form=form, words_number=num)


@app.route("/word_bank/user/<int:user_id>")
def word_bank_user(user_id):
    form = SearchForm()
    if form.validate_on_submit and form.search_data.data is not None:
        return redirect(url_for('word_bank_search', search_term=form.search_data.data))
    else:
        words = Word.query.filter_by(user_id=user_id).all()
        num = str(len(words))
    return render_template('word_bank.html', words=words, form=form, words_number=num)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = flask_bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!  You can log in now', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and flask_bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login unsuccessful.  Please check email and password.', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated.', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)


@app.route("/admin")
@login_required
def admin():
    today = datetime.date(datetime.now())
    unpublished = Word.query.filter(Word.date_published == None).all()
    return render_template('admin.html', title='Admin', unpublished=unpublished)


@app.route("/word/<int:word_id>")
def word(word_id):
    word = Word.query.get_or_404(word_id)
    return render_template('word.html', title=word.word, word=word, user=current_user)


@app.route("/word/new", methods=['GET', 'POST'])
def new_word():
    form = WordForm()
    form.get_parts_of_speech()
    if form.validate_on_submit():
        if form.part_o_speech.data == -1:
            flash(f'Please choose a part of speech.', 'fail')
        else:
            dupe = Word.query.filter(Word.word == form.word.data
                                     and Word.partOfSpeech_id == form.part_o_speech.data).first()
            if dupe:
                flash(f'This word was added on {dupe.date_published.strftime("%Y-%m-%d")}, you cretin.', 'fail')
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
                flash('Word added, you sot.', 'success')
                return redirect(url_for('home'))
    return render_template('word_upsert.html'
                           , title='Add Word'
                           , form=form
                           , legend='Add word'
                           , user=current_user)


@app.route("/word/<int:word_id>/update", methods=['GET', 'POST'])
@login_required
def update_word(word_id):
    word = Word.query.get_or_404(word_id)
    if word.contributor != current_user and current_user.isAdmin is False:
        abort(403)
    form = WordForm()
    form.get_parts_of_speech()
    flash(f'word thing {word.part_o_speech}', 'success')
    flash(f'form thing {form.part_o_speech.data}', 'success')
    if form.validate_on_submit():
        if form.part_o_speech.data == -1:
            flash('Please choose part of speech', 'fail')
        else:
            dupe = Word.query.filter(Word.id != word.id
                                     , Word.word == form.word.data
                                     , Word.partOfSpeech_id == form.part_o_speech.data).first()
            if dupe:
                flash(f'This word ({dupe.id}) was added on {dupe.date_published.strftime("%Y-%m-%d")}, you cretin.'
                      , 'fail')
            else:
                word.word = form.word.data
                word.partOfSpeech_id = form.part_o_speech.data
                word.definition = form.definition.data
                word.exampleSentence = form.exampleSentence.data
                word.ipa = form.ipa.data
                word.date_published = form.date_published.data
                word.contributor = current_user
                db.session.commit()
                flash('Word updated, you miscreant.', 'success')
                return redirect(url_for('word', word_id=word.id))
    elif form.is_submitted() and form.validate() is False:
        flash(f'this form failed', 'success')
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


@app.route("/word/<int:word_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_word(word_id):
    word = Word.query.get_or_404(word_id)
    if word.contributor != current_user and current_user.isAdmin:
        abort(403)
    db.session.delete(word)
    db.session.commit()
    flash('Your word has been deleted, the poor thing.', 'success')
    return redirect(url_for('home'))


'''
#may come back to add in commenting functions later on
@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Post created, you sot.', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post', form=form, legend='Create Post', user=current_user)


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Post updated, you miscreant.', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post', form=form, legend='Update Post')


@app.route("/delete_post/<int:post_id>/update", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted, the poor thing.', 'success')
    return redirect(url_for('home'))
'''
