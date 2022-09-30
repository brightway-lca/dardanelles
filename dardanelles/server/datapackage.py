from pathlib import Path
from bw_processing.io_helpers import file_reader, generic_zipfile_filesystem
from mimetypes import guess_type
from typing import Union
from bw_processing.errors import InvalidMimetype


class Datapackage:
    def __init__(self, filepath: Union[str, Path]):
        fp = Path(filepath)
        assert fp.exists()
        self.fs = generic_zipfile_filesystem(dirpath=fp.parent, filename=fp.name, write=False)
        self.metadata = file_reader(
            fs=self.fs, resource="datapackage.json", mimetype="application/json"
        )
        self.resources = self.metadata['resources']
        self.data = []
        for resource in self.resources:
            try:
                self.data.append(
                    file_reader(
                        fs=self.fs,
                        resource=resource["path"],
                        mimetype=resource["mediatype"],
                    )
                )
            except (InvalidMimetype, KeyError):
                raise InvalidMimetype

        self.depends = self.metadata['depends']
        self.database = self.metadata['database']
        self.name = self.metadata['name']
        self.description = self.metadata['description']

        index = [i for i, dct in enumerate(self.resources) if dct['path'] == 'nodes.csv']
        if not len(index) == 1:
            raise ValueError("Datapackage is missing `nodes.csv`")
        self.nodes = self.data[index[0]]

        index = [i for i, dct in enumerate(self.resources) if dct['path'] == 'edges.csv']
        if not len(index) == 1:
            raise ValueError("Datapackage is missing `edges.csv`")
        self.edges = self.data[index[0]]
