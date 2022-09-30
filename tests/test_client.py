from dardanelles.client.client import DardanellesClient


def test_client():
    d = DardanellesClient(api_key="no_key")

    # check alive
    assert d.alive

    # catalog
    expected_catalog = [
        [
            "c39e72a1c5384abe.Mobility-example.dfecf5bd.zip",
            "Mobility example",
            "c97eb0451c834e6feda05bcb321a4fde23725a31e3317d4ba4fa955342caead6",
        ],
        [
            "9998251db8e9402e.US-EEIO-11.59a428ab.zip",
            "US EEIO 1.1",
            "73f0af2315839131793deb544013d71e4570c3b181b20e16c3d5dbfff45d773c",
        ],
    ]
    assert d.catalog() == expected_catalog

    # importer
    d.importer_from_hash(expected_catalog[0][2])
    pass
