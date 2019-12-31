from xlsx2csv import Xlsx2csv
from werkzeug.utils import secure_filename
from partner.rosters.RosterToDb import RosterToDb
from partner import app
import os

ALLOWED_EXTENSIONS = {'xlsx'}

def process_roster_file_upload(file, section):
    if file and _allowed_file(file.filename):
        filename = secure_filename(file.filename)
        uploaded_filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        csv_filename = _filename_prefix(uploaded_filename) + '.' + 'csv'
        file.save(uploaded_filename)
        Xlsx2csv(uploaded_filename, outputencoding="utf-8").convert(csv_filename)
        # rdb = RosterToDb(section.id, csv_filename)
        # roster = rdb.roster
        # section.roster = roster
        return RosterToDb.create_roster(section,csv_filename)

def _filename_prefix (filename):
    return filename.rsplit('.', 1)[0]

def _allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS