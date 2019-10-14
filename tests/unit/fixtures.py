import pytest
from veides.sdk.agent import AgentClient, AgentProperties, ConnectionProperties


@pytest.fixture()
def connected_client():
    client = AgentClient(
        AgentProperties(client_id='some_id', key='', secret_key=''),
        ConnectionProperties(host='')
    )
    client.connected.set()

    return client
