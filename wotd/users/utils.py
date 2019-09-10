import os
import random
import image
from flask import url_for, current_app
from wotd import mail
from flask_mail import Message


def save_picture(form_file, folder_name):
    random_hex = random.token_hex(8)
    _, f_ext = os.path.splitext(form_file.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static', folder_name, picture_fn)

    output_size = (125, 125)
    i = image.open(form_file)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Brichword - Password Reset Request'
                  , sender='brichword@gmail.com'
                  , recipients=[user.email])
    msg.body = '''To reset your password, visit this link:
{}    
If you did not make this request, then simply ignore this email.
'''.format(url_for('reset_token', token=token, _external=True))
    mail.send(msg)
