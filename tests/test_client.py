from dardanelles.client.client import DardanellesClient

def test_client():
    d = DardanellesClient(api_key='no_key')

    # check alive
    assert d.alive

    pass