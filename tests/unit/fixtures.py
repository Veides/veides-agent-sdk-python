import pytest
from veides.sdk.agent import AgentClient, AgentProperties, ConnectionProperties


@pytest.fixture()
def agent_key():
    return 'some_key'


@pytest.fixture()
def agent_secret_key():
    return 'some_secret_key'


@pytest.fixture()
def hostname():
    return 'hostname'


@pytest.fixture()
def mocked_paho_client(mocker):
    class MockedPahoClient:
        connect = mocker.stub("connect")
        disconnect = mocker.stub("disconnect")
        loop_start = mocker.stub("loop_start")
        loop_stop = mocker.stub("loop_stop")
        username_pw_set = mocker.stub("username_pw_set")
        tls_set_context = mocker.stub("tls_set_context")
        message_callback_add = mocker.stub("message_callback_add")
        publish = mocker.stub("publish")
        subscribe = mocker.stub("subscribe")

    return MockedPahoClient()


@pytest.fixture()
def connected_client(mocker, mocked_paho_client, agent_key, agent_secret_key, hostname):
    mocker.patch("paho.mqtt.client.Client", return_value=mocked_paho_client)

    client = AgentClient(
        AgentProperties(client_id='some_id', key=agent_key, secret_key=agent_secret_key),
        ConnectionProperties(host=hostname)
    )
    client.connected.set()

    return client


@pytest.fixture()
def not_connected_client(mocker, mocked_paho_client, agent_key, agent_secret_key, hostname):
    mocker.patch("paho.mqtt.client.Client", return_value=mocked_paho_client)

    client = AgentClient(
        AgentProperties(client_id='some_id', key=agent_key, secret_key=agent_secret_key),
        ConnectionProperties(host=hostname)
    )

    return client
