from datetime import datetime
from sqlalchemy import and_, or_
from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import current_user, login_required
from wotd import db
from wotd.models import User, Word, Content
from wotd.admin.import_file import import_file
from wotd.admin.forms import FileForm, ContentForm
from wotd.main.forms import SearchForm
from wotd.admin.utils import save_file

admins = Blueprint('admins', __name__)


@admins.route("/admin", methods=['GET', 'POST'])
@login_required
def admin():
    if current_user.isAdmin is False:
        return redirect(url_for('main.home'))
    content = Content.query.filter_by(isActive=True).first()
    cid = content.id if content else 0
    form = SearchForm()
    if form.validate_on_submit and form.search_data.data is not None:
        return redirect(url_for('admins.admin_search', search_term=form.search_data.data))
    today = datetime.date(datetime.now())
    word_page = request.args.get('page', 1, type=int)
    future = Word.query \
        .filter(
            or_(
                Word.date_published == None
                , Word.date_published > today
            )
        ) \
        .paginate(per_page=5, page=word_page)
    user_page = request.args.get('page', 1, type=int)
    users = User.query.paginate(per_page=5, page=user_page)
    return render_template('admin.html'
                           , title='Admin'
                           , unpublished=future
                           , users=users
                           , form=form
                           , content_id=cid)


@admins.route("/admins/search/<string:search_term>", methods=['GET', 'POST'])
@login_required
def admin_search(search_term):
    if current_user.isAdmin is False:
        return redirect(url_for('main.home'))
    content = Content.query.filter_by(isActive=True).first()
    if content is None:
        cid = 0
    else:
        cid = content.id
    form = SearchForm()
    if form.validate_on_submit and form.search_data.data is not None:
        return redirect(url_for('admins.admin_search', search_term=form.search_data.data))
    today = datetime.date(datetime.now())
    search_term = '%' + search_term.lower() + '%'
    word_page = request.args.get('page', 1, type=int)
    future = Word.query \
        .filter(
            and_(
                    or_(
                        Word.date_published == None
                        , Word.date_published > today
                    )
                    , or_(
                        (Word.word.ilike(search_term))
                        , (Word.definition.ilike(search_term))
                        , (Word.exampleSentence.ilike(search_term))
                )
            )
        ) \
        .paginate(per_page=5, page=word_page)
    user_page = request.args.get('page', 1, type=int)
    users = User.query\
        .filter(or_((User.username.ilike(search_term)), (User.email.ilike(search_term))))\
        .paginate(per_page=5, page=user_page)
    return render_template('admin.html'
                           , title='admins'
                           , unpublished=future
                           , users=users
                           , form=form
                           , content_id=cid)


@admins.route("/content/new", methods=['GET', 'POST'])
@login_required
def content_new():
    if current_user.isAdmin is False:
        return redirect(url_for('main.home'))
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
            return redirect('admins')
    return render_template('content_upsert.html', title='Update Content', form=form)


@admins.route("/content/update/<int:content_id>", methods=['GET', 'POST'])
@login_required
def content_update(content_id):
    if current_user.isAdmin is False:
        return redirect(url_for('main.home'))
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
        return redirect(url_for('admins.admins'))
    elif request.method == 'GET':
        form.title.data = content.title
        form.private_title.data = content.private_title
        form.content.data = content.content
        form.isActive.data = content.isActive
    return render_template('content_upsert.html', title='Update Content', form=form)


@admins.route("/import_words", methods=['GET', 'POST'])
@login_required
def import_words():
    if current_user.isAdmin is False:
        return redirect(url_for('main.home'))
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

