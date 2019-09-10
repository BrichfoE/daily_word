import json
import datetime
from wotd.models import Word, PartOfSpeech, User
from wotd import db


def import_file(upload_file):
    file = open(upload_file, "r")
    text = file.read()
    count = 0
    parts = PartOfSpeech.query.all()
    admin = User.query.first()
    import_list = json.loads(text)
    addition_list = []
    exception_list = []
    for key in import_list:
        word_check = Word.query.filter_by(word=key).first()
        error = ''
        if word_check is None:
            try:
                error='Word()'
                newWord = Word()
                newWord.word = import_list[key]['word']
                # newWord.id = importList[key]['id'] # no need, this is the primary key
                error='Dates'
                newWord.date_published = datetime.datetime.strptime(import_list[key]['date_published'], '%Y-%m-%dT%H:%M:%S')
                newWord.date_added = datetime.datetime.strptime(import_list[key]['date_added'], '%Y-%m-%dT%H:%M:%S')
                error='Part of Speech'
                newWord.part_o_speech = parts[import_list[key]['partOfSpeech']]
                error='Details'
                newWord.definition = import_list[key]['definition']
                newWord.ipa = import_list[key]['ipa']
                newWord.exampleSentence = import_list[key]['exampleSentence']
                error='User'
                newWord.contributor = admin
                count += 1
                addition_list.append(import_list[key]['word'])
                db.session.add(newWord)
            except:
                print('Issue loading {}'.format(key))
                exception_list.append([key, error])
    print('Adding {} new words'.format(count))
    db.session.commit()
    return addition_list, exception_list


# for test
#errors = import_file("C:/git/daily_word/building/import.txt")

