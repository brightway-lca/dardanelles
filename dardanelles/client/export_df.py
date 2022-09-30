import datetime
import uuid
from pathlib import Path
from typing import Optional

import numpy as np
from bw2data import Database, databases
from bw_processing.constants import DEFAULT_LICENSES
from bw_processing.filesystem import clean_datapackage_name, safe_filename
from bw_processing.io_helpers import file_writer, generic_zipfile_filesystem
from bw_processing.utils import check_name, check_suffix


def to_dardanelles_datapackage(
    database: str,
    author: str,
    description: str,
    add_uncertainty: bool = True,
    directory: Optional[Path] = None,
    version: Optional[str] = None,
    id_: Optional[str] = None,
    licenses: Optional[list] = None,
):
    """Export a Brightway database to a zipped datapackage in a temporary directory.

    * ``database``: str. Name of database to export.
    * ``add_uncertainty``: bool, default ``True``. Add uncertainty columns to edges.
    * ``metadata``: dict for author, license, version

    """
    if database not in databases:
        raise ValueError(f"The given database {database} can't be found")

    db = Database(database)

    if not len(db):
        raise ValueError(f"The given database {database} is empty")

    dirpath = Path(directory or Path.cwd())

    def add_uncertainty_columns(node, edge, row):
        fields = (
            "uncertainty_type",
            "loc",
            "scale",
            "shape",
            "minimum",
            "maximum",
            "negative",
        )
        for field in fields:
            row[field] = edge.get(field)

    formatters = [add_uncertainty_columns] if add_uncertainty else []

    name = clean_datapackage_name(database)
    check_name(name)

    metadata = {
        "profile": "tabular-data-package",
        "name": name,
        "database": database,
        "description": description,
        "id": id_ or uuid.uuid4().hex,
        "licenses": licenses or DEFAULT_LICENSES,
        "resources": [],
        "depends": db.metadata["depends"],
        "created": datetime.datetime.utcnow().isoformat("T") + "Z",
    }

    # Numpy dtypes are "interesting", can't just lookup in a dict
    # but can test for equality
    # https://stackoverflow.com/questions/26921836/correct-way-to-test-for-numpy-dtype
    mapping = [
        (int, "number"),
        (np.int_, "number"),
        (np.integer, "number"),
        (np.int32, "number"),
        (np.int64, "number"),
        (object, "string"),
        (np.object_, "string"),
        (str, "string"),
        (np.bool_, "boolean"),
        (bool, "boolean"),
        (np.float_, "number"),
        (np.float32, "number"),
        (np.float64, "number"),
    ]

    def get_dtype(dtype):
        for x, y in mapping:
            if x == dtype:
                return y
        raise ValueError(f"Can't understand dtype {dtype}")

    filename = check_suffix(safe_filename(database), "zip")
    zipfile = generic_zipfile_filesystem(dirpath=dirpath, filename=filename, write=True)

    df = db.nodes_to_dataframe()
    resource = {
        "path": "nodes.csv",
        "profile": "tabular-data-resource",
        "mediatype": "text/csv",
        "schema": {
            "primaryKey": "id",
            "fields": [
                {
                    "name": label,
                    "type": get_dtype(dtype),
                }
                for label, dtype in zip(df.columns, df.dtypes)
            ],
        },
    }
    metadata["resources"].append(resource)
    file_writer(data=df, fs=zipfile, resource="nodes.csv", mimetype="text/csv")

    df = db.edges_to_dataframe(categorical=False, formatters=formatters)
    resource = {
        "path": "edges.csv",
        "profile": "tabular-data-resource",
        "mediatype": "text/csv",
        "schema": {
            "fields": [
                {
                    "name": label,
                    "type": get_dtype(dtype),
                }
                for label, dtype in zip(df.columns, df.dtypes)
            ]
        },
    }
    metadata["resources"].append(resource)
    file_writer(data=df, fs=zipfile, resource="edges.csv", mimetype="text/csv")

    file_writer(
        data=metadata,
        fs=zipfile,
        resource="datapackage.json",
        mimetype="application/json",
    )
    zipfile.close()

    return dirpath / filename
