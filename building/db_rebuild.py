from flask import Flask
from flask_bcrypt import Bcrypt
from wotd import db
from wotd.models import Word, User, PartOfSpeech
from building.import_file import import_file

app = Flask(__name__)
flask_bcrypt = Bcrypt(app)

db.drop_all()
db.session.commit()

parts = [PartOfSpeech(id=1, partOfSpeech='noun')
        , PartOfSpeech(id=2, partOfSpeech='adjective')
        , PartOfSpeech(id=3, partOfSpeech='verb')
        , PartOfSpeech(id=4, partOfSpeech='adverb')]


password = 'admin_init'
hashed_password = flask_bcrypt.generate_password_hash(password).decode('utf-8')
user = User(username="Admin"
            ,email="ebrichford@gmail.com"
            , password=hashed_password
            , isAdmin=True)

db.create_all()
db.session.commit()

db.session.add(user)
for p in parts:
    db.session.add(p)

db.session.commit()

errors = import_file("C:/git/daily_word/building/import.txt")
