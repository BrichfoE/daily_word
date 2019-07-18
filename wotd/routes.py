import os
import secrets
from datetime import datetime
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from wotd import app, db, flask_bcrypt
from wotd.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, WordForm
from wotd.models import User, Post, Word
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


@app.route("/wordbank")
def wordbank():
    words = Word.query.all()
    return render_template('word_bank.html', words=words)


@app.route("/random")
def random():
    words = Word.query.all()
    return render_template('word_bank.html', words=words)


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


@app.route("/word/new", methods=['GET', 'POST'])
@login_required
def new_word():
    form = WordForm()
    if form.validate_on_submit():
        word = Word(word=form.word.data
                    , partOfSpeech=form.partOfSpeech.data
                    , definition=form.definition.data
                    , exampleSentence=form.exampleSentence.data
                    , ipa=form.ipa.data
                    , date_published=form.date_published.data
                    , contributor=current_user)
        db.session.add(word)
        db.session.commit()
        flash('Word added, you sot.', 'success')
        return redirect(url_for('home'))
    return render_template('word_upsert.html', title='Add Word', form=form, legend='Add word')


@app.route("/word/<int:word_id>")
def word(word_id):
    word = Word.query.get_or_404(word_id)
    return render_template('word.html', title=word.word, word=word)


@app.route("/word/<int:word_id>/update", methods=['GET', 'POST'])
@login_required
def update_word(word_id):
    word = Word.query.get_or_404(word_id)
    if word.contributor != current_user and current_user.isAdmin:
        abort(403)
    form = WordForm()
    if form.validate_on_submit():
        word.word = form.word.data
        word.partOfSpeech = form.partOfSpeech.data
        word.definition = form.definition.data
        word.exampleSentence = form.exampleSentence.data
        word.ipa = form.ipa.data
        word.date_published = form.date_published.data
        word.contributor = current_user
        db.session.commit()
        flash('Word updated, you miscreant.', 'success')
        return redirect(url_for('word', word_id=word.id))
    elif request.method == 'GET':
        form.word.data = word.word
        form.partOfSpeech.data = word.partOfSpeech
        form.definition.data = word.definition
        form.exampleSentence.data = word.exampleSentence
        form.ipa.data = word.ipa
        form.date_published.data = word.date_published
    return render_template('word_upsert.html', title='Update ' + word.word, form=form, legend='Update Word')


@app.route("/word/<int:word_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_word(word_id):
    word = Word.query.get_or_404(word_id)
    if word.contributor != current_user:
        abort(403)
    db.session.delete(word)
    db.session.commit()
    flash('Your word has been deleted, the poor thing.', 'success')
    return redirect(url_for('home'))


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
    return render_template('create_post.html', title='New Post', form=form, legend='Create Post')


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
