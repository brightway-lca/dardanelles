from bw2io.importers.base_lci import LCIImporter
from bw2io.strategies import tupleize_categories


class DardanellesImporter(LCIImporter):
    def __init__(self, data, metadata):
        super().__init__(metadata["database"])
        self.strategies = [tupleize_categories] + self.strategies
        self.data = data
        self.metadata = metadata
