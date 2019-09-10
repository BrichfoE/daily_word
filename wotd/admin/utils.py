import os
import random
from flask import current_app


def save_file(form_file, folder_name):
    random_hex = random.token_hex(8)
    _, f_ext = os.path.splitext(form_file.filename)
    file_fn = random_hex + f_ext
    file_path = os.path.join(current_app.root_path, 'static', folder_name, file_fn)
    form_file.save(file_path)

    return file_path
