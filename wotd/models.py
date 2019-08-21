from datetime import datetime
from wotd import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    isAdmin = db.Column(db.Boolean, nullable=False, default=False)
    words = db.relationship('Word', backref='contributor', lazy=True)
    # posts = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class PartOfSpeech(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    partOfSpeech = db.Column(db.String(100), nullable=False)
    words = db.relationship('Word', backref='part_o_speech', lazy=True)

    def __repr__(self):
        return f"{self.partOfSpeech}"


class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(100), nullable=False)
    #part_o_speech = db.Column(db.String(100), nullable=False)
    partOfSpeech_id = db.Column(db.Integer, db.ForeignKey('part_of_speech.id'), nullable=False)
    definition = db.Column(db.Text, nullable=False)
    exampleSentence = db.Column(db.Text, nullable=False)
    ipa = db.Column(db.Text, nullable=True)
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_published = db.Column(db.Date, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def __repr__(self):
        return f"Word('{self.word}', '{self.part_o_speech}', '{self.contributor}')"#", ''{self.date_published.strftime('%Y-%m-%d')}')"


class Content(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    private_title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    isActive = db.Column(db.Boolean, nullable=False, default=False)


'''
#may come back to allow commenting in-app later on
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"
'''
