import tempfile
from numbers import Number
from pathlib import Path
from typing import Optional

import bcrypt
import numpy as np
import requests
import wrapt

from ..datapackage import Datapackage
from .errors import AlreadyExists, RemoteError
from .export_df import to_dardanelles_datapackage
from .import_class import DardanellesImporter
from .utils import sha256

try:
    from bw2io.download_utils import download_with_progressbar
except ImportError:
    from .utils import download_with_progressbar


DEFAULT_SALT = b"$2b$12$1FBcxtAiJUHWbTxY/47O1u"


@wrapt.decorator
def check_alive(wrapped, instance, args, kwargs):
    if not instance.alive:
        raise RemoteError("Can't reach {}".format(instance.url))
    return wrapped(*args, **kwargs)


def register(
    email: str,
    username: str,
    url: Optional[str] = "https://lci.brightway.dev",
    salt: Optional[bytes] = DEFAULT_SALT,
):
    data = {
        "email_hash": bcrypt.hashpw(bytes(email, "utf-8"), salt),
        "username": username,
    }
    resp = requests.post(url + "/register", data=data)
    if resp.status_code == 200:
        return resp.json()["api_key"]
    else:
        raise RemoteError


def reformat_edge(dct: dict, nodes: list):
    stripper = lambda x: x.replace("source_", "") if x.startswith("source_") else x

    try:
        node = nodes[dct["source_id"]]
        dct["input"] = (node["database"], node["code"])
    except KeyError:
        pass

    target = dct.pop("target_id")
    dct = {stripper(k): v for k, v in dct.items() if not k.startswith("target_")}
    dct["amount"] = dct.pop("edge_amount")
    dct["type"] = dct.pop("edge_type")
    return target, dct


def clean_dict(dct: dict):
    notnan = lambda x: not isinstance(x, Number) or not np.isnan(x)
    hasvalue = lambda x: bool(x) or x == 0
    return {k: v for k, v in dct.items() if notnan(v) and hasvalue(v)}


class DardanellesClient:
    def __init__(self, api_key: str, url: str = "https://lci.brightway.dev"):
        self.url = url
        self.api_key = api_key
        while self.url.endswith("/"):
            self.url = self.url[:-1]

    @property
    def alive(self):
        return requests.get(self.url + "/ping").status_code == 200

    @check_alive
    def catalog(self):
        return requests.get(self.url + "/catalog").json()

    @check_alive
    def upload_database(
        self,
        database: str,
        author: str,
        description: str,
        add_uncertainty: bool = True,
        version: Optional[str] = None,
        id_: Optional[str] = None,
        licenses: Optional[list] = None,
    ):
        with tempfile.TemporaryDirectory() as td:
            filepath = to_dardanelles_datapackage(
                database=database,
                author=author,
                description=description,
                add_uncertainty=add_uncertainty,
                directory=td,
                version=version,
                id_=id_,
                licenses=licenses,
            )
            self._upload(filepath, database)

    def _upload(self, filepath: str, database: str):
        file_hash = sha256(filepath)
        url = self.url + "/upload"
        data = {
            "api_key": self.api_key,
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

    def importer_from_hash(self, file_hash: str):
        with tempfile.TemporaryDirectory() as td:
            fp = download_with_progressbar(
                url=self.url + "/download/" + file_hash, dirpath=td
            )
            dp = Datapackage(fp)
            data = {
                obj["id"]: clean_dict(obj)
                for obj in dp.nodes.to_dict("records")
            }
            for dct in data.values():
                dct["exchanges"] = []

            for row in dp.edges.to_dict("records"):
                id_, exc = reformat_edge(row, data)
                data[id_]["exchanges"].append(exc)

            return DardanellesImporter(
                data={(obj["database"], obj["code"]): obj for obj in data.values()},
                metadata=dp.metadata,
            )
