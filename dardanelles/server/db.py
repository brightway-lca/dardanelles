from .filesystem import data_dir
from peewee import (
    Model,
    SqliteDatabase,
    TextField,
)
import os


db_filepath = os.path.join(data_dir, "dardanelles.db")
print("Using database at", db_filepath)
database = SqliteDatabase(db_filepath)


class File(Model):
    filepath = TextField()
    sha256 = TextField(unique=True)
    database = TextField()


database.create_tables([File], safe=True)
