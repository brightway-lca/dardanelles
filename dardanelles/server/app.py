import hashlib
import json
import uuid
from pathlib import Path

from flask import Response, abort, render_template, request, send_file, url_for
from peewee import DoesNotExist
from werkzeug.utils import secure_filename

from ..datapackage import Datapackage
from ..version import version
from . import dardanelles_app
from .db import File, User
from .filesystem import data_dir


def sha256(filepath, blocksize=65536):
    """Generate SHA 256 hash for file at `filepath`"""
    hasher = hashlib.sha256()
    fo = open(filepath, "rb")
    buf = fo.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = fo.read(blocksize)
    return hasher.hexdigest()


def json_response(data):
    return Response(json.dumps(data), mimetype="application/json")


@dardanelles_app.route("/")
def index():
    return render_template("index.html", table=File.select())


@dardanelles_app.route("/ping")
def ping():
    return "pong"


@dardanelles_app.route("/register", methods=["POST"])
def register():
    if not request.form["email_hash"] or not request.form["username"]:
        abort(400, "Missing required field")

    email_hash = request.form["email_hash"]
    name = request.form["username"]

    if (
        User.select()
        .where((User.email_hash != email_hash) & (User.name == name))
        .exists()
    ):
        abort(406, "Username already registered")

    try:
        user = User.get(User.email_hash == email_hash)
    except User.DoesNotExist:
        api_key = uuid.uuid4().hex
        user = User.create(email_hash=email_hash, api_key=api_key, name=name)

    return json_response({"api_key": api_key})


@dardanelles_app.route("/catalog")
def catalog():
    return json_response(
        [(Path(obj.filepath).name, obj.database, obj.sha256) for obj in File.select()]
    )


@dardanelles_app.route("/download/<hash>", methods=["GET"])
def download(hash):
    try:
        obj = File.get(File.sha256 == hash)
    except DoesNotExist:
        abort(404, "Can't find file")

    return send_file(
        obj.filepath,
        mimetype="application/octet-stream",
        as_attachment=True,
        download_name=Path(obj.filepath).name,
    )


@dardanelles_app.route("/upload", methods=["POST"])
def upload():
    if (
        not request.form["sha256"]
        or not request.form["database"]
        or not request.form["filename"]
        or not request.form["api_key"]
    ):
        abort(400, "Missing required field(s)")

    try:
        user = User.get(User.api_key == request.form["api_key"])
    except User.DoesNotExist:
        abort(406, "api_key not correct")

    their_hash = request.form["sha256"]
    filename = secure_filename(request.form["filename"])
    database = request.form["database"]
    file_obj = request.files["file"]
    new_name = uuid.uuid4().hex[:16] + "." + filename
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

    try:
        dp = Datapackage(filepath)
        assert len(dp.nodes)
    except:
        filepath.unlink()
        abort(406, "Can't load datapackage")

    File(
        user=user,
        filepath=str(filepath),
        database=database,
        depends=dp.depends,
        description=dp.description,
        sha256=our_hash,
    ).save()

    return json_response({"filename": new_name, "sha256": our_hash})
