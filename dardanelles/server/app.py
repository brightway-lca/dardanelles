from . import dardanelles_app
from .db import File
from .filesystem import data_dir
from flask import (
    abort,
    request,
    Response,
    send_file,
    url_for,
)
from peewee import DoesNotExist
from werkzeug.utils import secure_filename
import json
import uuid
from ..version import version
import hashlib


def sha256(filepath, blocksize=65536):
    """Generate SHA 256 hash for file at `filepath`"""
    hasher = hashlib.sha256()
    fo = open(filepath, 'rb')
    buf = fo.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = fo.read(blocksize)
    return hasher.hexdigest()


def json_response(data):
    return Response(json.dumps(data), mimetype='application/json')


@dardanelles_app.route('/')
def index():
    return """dardanelles web service, version {}.""".format(version)


@dardanelles_app.route('/ping')
def ping():
    return "pong"


@dardanelles_app.route('/catalog')
def catalog():
    return json_response([(Path(obj.filepath).name, obj.database, obj.sha256) for obj in File.select()])


@dardanelles_app.route('/download', methods=['POST'])
def download():
    filehash = request.form['hash']

    try:
        obj = File.get(File.sha256 == filehash)
    except DoesNotExist:
        abort(404, "Can't find file")

    return send_file(
        obj.filepath,
        mimetype='application/octet-stream',
        as_attachment=True,
        attachment_filename=Path(obj.filepath).name
    )


@dardanelles_app.route('/upload', methods=['POST'])
def upload():
    if not request.form['sha256'] or not request.form['database'] or not request.form['filename']:
        abort(400, "Missing required field(s)")

    their_hash = request.form['sha256']
    filename = secure_filename(request.form['filename'])
    database = request.form['database']
    file_obj = request.files['file']
    new_name = uuid.uuid4().hex + "." + filename
    filepath = data_dir / "uploads" / new_name
    file_obj.save(filepath)
    our_hash = sha256(filepath)

    # Provided hash is incorrect
    if our_hash != their_hash:
        filepath.unlink()
        abort(406, "Can't reproduce provided hash value")

    # Hash already exists
    if File.select().where(File.sha256 == our_hash).count():
        filepath.unlink()
        abort(409, "This file hash is already uploaded")

    File(
        filepath=str(filepath),
        name=new_name,
        sha256=our_hash,
    ).save()

    return json_response(
        {
            'filename': new_name,
            'sha256': our_hash
        }
    )
