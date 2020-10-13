from flask_login import login_required, current_user, logout_user
import os
import errno
import zipfile
from werkzeug.utils import secure_filename

from flask import request, jsonify
from partner import app
# REST API endpoint to get a roster (students plus attendance data for given date) as JSON.
@app.route('/rest/grading', methods=['POST'])
# @login_required
def grading():
    print("in grading")
    files = request.files.getlist('files[]')
    zip_file = [f for f in files if f.content_type == 'application/zip']
    unit_test = [f for f in files if f.content_type != 'application/zip']
    if len(zip_file) > 0:
        path = process_file_upload(zip_file[0], 'zip')
        unzip_file(path)

    if len(unit_test) > 0:
        process_file_upload(unit_test[0], 'py')
    try:
        rubric = request.form.get('rubric')
    except Exception as e:
        print("Loading JSON", str(e))
    print(f'{rubric}')
    return jsonify({})

def filename_prefix(filename):
    return filename.rsplit('.', 1)[0]


def allowed_file(filename, ext):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() == ext

def process_file_upload(file, ext):
    if file and allowed_file(file.filename, ext):
        secure = secure_filename(file.filename)
        uploaded_filename = os.path.join(app.config['UPLOAD_FOLDER'], secure)
        filename = filename_prefix(uploaded_filename) + '.' + ext
        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        file.save(uploaded_filename)
        return uploaded_filename
    else:
        return None

def unzip_file (file, dir):
    with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
        zip_ref.extractall(directory_to_extract_to)