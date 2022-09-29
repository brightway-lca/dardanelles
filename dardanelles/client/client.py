import requests
import wrapt
from .errors import RemoteError, AlreadyExists
from .export_df import to_dardanelles_datapackage
import tempfile
from pathlib import Path
from .utils import sha256
from typing import Optional


@wrapt.decorator
def check_alive(wrapped, instance, args, kwargs):
    if not instance.alive:
        raise RemoteError("Can't reach {}".format(instance.url))
    return wrapped(*args, **kwargs)


class DardanellesClient:
    def __init__(self, url: str="https://lci.brightway.dev"):
        self.url = url
        while self.url.endswith("/"):
            self.url = self.url[:-1]

    @property
    def alive(self):
        return requests.get(self.url + "/ping").status_code == 200

    @check_alive
    def catalog(self):
        return requests.get(self.url + "/catalog").json()

    @check_alive
    def upload_database(self, database: str, author: str, add_uncertainty: bool=True, version: Optional[str] = None, id_: Optional[str] = None, licenses: Optional[list] = None):
        with tempfile.TemporaryDirectory() as td:
            filepath = to_dardanelles_datapackage(database=database, author=author, add_uncertainty=add_uncertainty, directory=td, version=version, id_=id_, licenses=licenses)
            self._upload(filepath, database)

    def _upload(self, filepath: str, database: str):
        file_hash = sha256(filepath)
        url = self.url + "/upload"
        data = {
            "filename": filepath.name,
            "database": database,
            "sha256": sha256(filepath),
        }
        files = {"file": open(filepath, "rb")}
        resp = requests.post(url, data=data, files=files)
        if resp.status_code == 200:
            return resp.json()
        else:
            raise RemoteError("{}: {}".format(resp.status_code, resp.text))

