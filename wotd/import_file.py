import json
import datetime
from wotd.models import Word
from wotd import db


def import_file(file_name):
    file = open(file_name, "r")
    text = file.read()
    count = 0

    import_list = json.loads(text)
    exception_list = []

    for key in import_list:
        word_check = Word.query.filter_by(word=key).first()
        if word_check is None:
            try:
                count += 1
                newWord = Word()
                newWord.word = import_list[key]['word']
                # newWord.id = importList[key]['id'] # no need, this is the primary key
                newWord.date_published = datetime.datetime.strptime(import_list[key]['date_published'], '%Y-%m-%dT%H:%M:%S')
                newWord.date_added = datetime.datetime.strptime(import_list[key]['date_added'], '%Y-%m-%dT%H:%M:%S')
                newWord.partOfSpeech = import_list[key]['partOfSpeech']
                newWord.definition = import_list[key]['definition']
                newWord.ipa = import_list[key]['ipa']
                newWord.exampleSentence = import_list[key]['exampleSentence']
                newWord.user_id = 1
                db.session.add(newWord)
            except:
                print(f'Issue loading {key}')
                exception_list.append(key)
    print(f'Adding {count} new words')
    db.session.commit()

    return exception_list


# for test
errors = import_file("C:\git\WotD\import\import.txt")

