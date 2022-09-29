from .filesystem import data_dir
from peewee import (
    Model,
    SqliteDatabase,
    TextField,
    DateTimeField,
    IntegerField,
)
import os


db_filepath = os.path.join(data_dir, "dardanelles.db")
print("Using database at", db_filepath)
sql_database = SqliteDatabase(db_filepath)


class File(Model):
    filepath = TextField()
    sha256 = TextField(unique=True)
    database = TextField()
    created = DateTimeField(default=datetime.datetime.now)
    accessed = DateTimeField(default=datetime.datetime.now)
    count = IntegerField(default=0)

    class Meta:
        database = sql_database


sql_database.create_tables([File], safe=True)
