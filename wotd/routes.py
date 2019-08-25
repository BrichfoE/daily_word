import os
import random
from datetime import datetime
import image
from flask import render_template, url_for, flash, redirect, request, abort
from wotd import app, db, flask_bcrypt
from wotd.forms import RegistrationForm, LoginForm, UpdateAccountForm, WordForm, SearchForm, AdminAccountForm, FileForm, ContentForm
from wotd.models import User, Word, Content
from wotd.import_file import import_file
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
def home():
    today = datetime.date(datetime.now())
    form = SearchForm()
    if form.validate_on_submit and form.search_data.data is not None:
        return redirect(url_for('word_bank_search', search_term=form.search_data.data))
    elif Word.query.filter(Word.date_published == today).count() > 0:
        word = Word.query.filter(Word.date_published == today).first()
    else:
        word = Word()
        word.date_published = datetime.now().date()
    return render_template('home.html', word=word, form=form)


@app.route("/word_bank", methods=['GET', 'POST'])
def word_bank():
    form = SearchForm()
    if form.validate_on_submit and form.search_data.data is not None:
        return redirect(url_for('word_bank_search', search_term=form.search_data.data))
    else:
        words = Word.query.order_by(Word.date_published.desc()).limit(7)
        num = str(words.count())
    return render_template('word_bank.html', title='Word Bank', words=words, form=form, words_number=num)


@app.route("/word_bank/search/<string:search_term>", methods=['GET', 'POST'])
def word_bank_search(search_term):
    form = SearchForm()
    if form.validate_on_submit and form.search_data.data is not None:
        return redirect(url_for('word_bank_search', search_term=form.search_data.data))
    all_words = Word.query.order_by(Word.word).all()
    search_term = search_term.lower()
    words = [x for x in all_words
                if (search_term in x.word.lower()
                or search_term in x.definition.lower()
                or search_term in x.exampleSentence.lower())
                and x.date_published is not None]
    num = str(len(words))
    return render_template('word_bank.html', words=words, form=form, words_number=num)


@app.route("/word_bank/random")
def word_bank_random():
    form = SearchForm()
    if form.validate_on_submit and form.search_data.data is not None:
        return redirect(url_for('word_bank_search', search_term=form.search_data.data))
    else:
        max = Word.query.count()
        words = [Word()]
        while words[0].date_published is None:
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
        all_words = Word.query.filter_by(user_id=user_id).order_by(Word.word).all()
        words = [x for x in all_words if x.date_published is not None]
        num = str(len(words))
    return render_template('word_bank.html', words=words, form=form, words_number=num)


@app.route("/about")
def about():
    active = Content.query.filter_by(isActive=True).first()
    return render_template('about.html', title='About', content=active)


@app.route("/content/new", methods=['GET', 'POST'])
@login_required
def content_new():
    if current_user.isAdmin is False:
        return redirect(url_for('home'))
    else:
        form = ContentForm()
        if form.validate_on_submit():
            new_content = Content(
                title=form.title.data
                , private_title=form.private_title.data
                , content=form.content.data
                , isActive=form.isActive.data
            )
            if new_content.isActive is True:
                active = Content.query.filter_by(isActive=True).first()
                if active is not None:
                    active.isActive = False
            db.session.add(new_content)
            db.session.commit()
            flash('{} added!  Content is King!  That or Gidorah is King.  Either Or.'.format(new_content.title), 'success')
            return redirect('admin')
    return render_template('content_upsert.html', title='Update Content', form=form)


@app.route("/content/update/<int:content_id>", methods=['GET', 'POST'])
@login_required
def content_update(content_id):
    if current_user.isAdmin is False:
        return redirect(url_for('home'))
    form = ContentForm()
    content = Content.query.filter_by(id=content_id).first()
    if form.validate_on_submit():
        if form.isActive.data is True:
            active = Content.query.filter_by(isActive=True).first()
            if active is not None:
                active.isActive = False
        content.title = form.title.data
        content.private_title = form.private_title.data
        content.content = form.content.data
        content.isActive = form.isActive.data
        db.session.commit()
        flash('Content updated, now be content!', 'success')
        return redirect(url_for('admin'))
    elif request.method == 'GET':
        form.title.data = content.title
        form.private_title.data = content.private_title
        form.content.data = content.content
        form.isActive.data = content.isActive
    return render_template('content_upsert.html', title='Update Content', form=form)


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
        flash('Account created for {}!  You can log in now'.format(form.username.data), 'success')
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


def save_file(form_file, folder_name):
    random_hex = random.token_hex(8)
    _, f_ext = os.path.splitext(form_file.filename)
    file_fn = random_hex + f_ext
    file_path = os.path.join(app.root_path, 'static', folder_name, file_fn)
    form_file.save(file_path)

    return file_path


def save_picture(form_file, folder_name):
    random_hex = random.token_hex(8)
    _, f_ext = os.path.splitext(form_file.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static', folder_name, picture_fn)

    output_size = (125, 125)
    i = image.open(form_file)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data, 'profile_pics')
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
    return render_template('account.html', title='Account', image_file=image_file, form=form, adminView=False)


@app.route("/account/admin/<int:user_id>", methods=['GET', 'POST'])
@login_required
def account_admin(user_id):
    if current_user.isAdmin is False:
        return redirect(url_for('home'))
    form = AdminAccountForm()
    user = User.query.filter(User.id == user_id).first()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data, 'profile_pics')
            user.image_file = picture_file
        user.username = form.username.data
        user.email = form.email.data
        user.isAdmin = form.isAdmin.data
        db.session.commit()
        flash('Your account has been updated.', 'success')
        return redirect(url_for('admin_search', search_term=user.email))
    elif request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        form.isAdmin.data = user.isAdmin
    image_file = url_for('static', filename='profile_pics/' + user.image_file)
    default = url_for('static', filename='default.jpg')
    return render_template('account.html'
                           , title='Account - Admin'
                           , image_file=image_file
                           , image_default=default
                           , form=form
                           , adminView=True)


@app.route("/admin", methods=['GET', 'POST'])
@login_required
def admin():
    if current_user.isAdmin is False:
        return redirect(url_for('home'))
    content = Content.query.filter_by(isActive=True).first()
    if content is None:
        cid = 0
    else:
        cid = content.id
    form = SearchForm()
    if form.validate_on_submit and form.search_data.data is not None:
        return redirect(url_for('admin_search', search_term=form.search_data.data))
    today = datetime.date(datetime.now())
    all_words = Word.query.order_by(Word.date_published.desc()).all()
    future = [x for x in all_words if x.date_published == None or x.date_published > today]
    users = User.query.all()
    return render_template('admin.html'
                           , title='Admin'
                           , unpublished=future
                           , users=users
                           , form=form
                           , content_id=cid)


@app.route("/admin/search/<string:search_term>", methods=['GET', 'POST'])
def admin_search(search_term):
    if current_user.isAdmin is False:
        return redirect(url_for('home'))
    content = Content.query.filter_by(isActive=True).first()
    if content is None:
        cid = 0
    else:
        cid = content.id
    form = SearchForm()
    if form.validate_on_submit and form.search_data.data is not None:
        return redirect(url_for('admin_search', search_term=form.search_data.data))
    search_term = search_term.lower()
    today = datetime.date(datetime.now())
    all_words = Word.query.all()
    future = [x for x in all_words
                if (x.date_published is None
                or x.date_published > today)
                and (search_term in x.word.lower()
                or search_term in x.definition.lower()
                or search_term in x.exampleSentence.lower())]
    all_users = User.query.all()
    users = [y for y in all_users
                if search_term in y.username.lower()
                or search_term in y.email.lower()]
    return render_template('admin.html'
                           , title='Admin'
                           , unpublished=future
                           , users=users
                           , form=form
                           , content_id=cid)


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
                    flash('Word added, awaiting review and scheduling by a site admin, who is slow...', 'success')
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
                return redirect(url_for('word', word_id=word.id))
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


@app.route("/word/<int:word_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_word(word_id):
    word = Word.query.get_or_404(word_id)
    if word.contributor != current_user and current_user.isAdmin is False:
        abort(403)
    db.session.delete(word)
    db.session.commit()
    flash('Your word has been deleted, the poor thing.', 'success')
    return redirect(url_for('home'))


@app.route("/import_words", methods=['GET', 'POST'])
@login_required
def import_words():
    if current_user.isAdmin is False:
        return redirect(url_for('home'))
    form = FileForm()
    results = [], []
    if form.validate_on_submit():
        if form.file.data:
            file_path = save_file(form.file.data, 'import_files')
            results = import_file(file_path)
    add_count = 'Additions (' + str(len(results[0])) + ')'
    error_count = 'Errors (' + str(len(results[1])) + ')'
    return render_template('upload.html'
                           , title='Upload a File'
                           , form=form
                           , results=results
                           , add_count=add_count
                           , error_count=error_count)


