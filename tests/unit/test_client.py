import pytest
import json
from paho.mqtt.client import MQTTMessage, MQTT_ERR_SUCCESS
from tests.unit.fixtures import (
    connected_client,
    not_connected_client,
    mocked_paho_client,
    agent_key,
    agent_secret_key,
    hostname
)


def test_should_subscribe_to_base_topics_and_set_event_when_connected(not_connected_client, hostname):
    def side_effect(*_, **__):
        not_connected_client.client.on_connect(None, None, None, 0)

    not_connected_client.client.connect.side_effect = side_effect
    not_connected_client.client.subscribe.return_value = (MQTT_ERR_SUCCESS, None)
    not_connected_client.connect()

    not_connected_client.client.connect.assert_called_once_with(hostname, keepalive=60, port=8883)
    not_connected_client.client.loop_start.assert_called_once()
    not_connected_client.client.subscribe.assert_called_once_with(
        f'agent/{not_connected_client.client_id}/action_received',
        qos=1
    )
    assert not_connected_client.is_connected() is True


def test_should_stop_loop_and_clear_event_after_disconnect(connected_client):
    def side_effect(*_, **__):
        connected_client.client.on_disconnect(None, None, 0)

    connected_client.client.disconnect.side_effect = side_effect

    connected_client.disconnect()

    connected_client.client.disconnect.assert_called_once()
    connected_client.client.loop_stop.assert_called_once()
    assert connected_client.is_connected() is False


def test_should_setup_credentials(not_connected_client, agent_key, agent_secret_key):
    not_connected_client.client.username_pw_set.assert_called_once_with(agent_key, agent_secret_key)


def test_should_setup_tls_context(not_connected_client):
    not_connected_client.client.tls_set_context.assert_called_once()


def test_should_use_action_handler_when_action_received(mocker, connected_client):
    action_name = 'some_action'

    msg = MQTTMessage()
    msg.topic = f'agent/{connected_client.client_id}/action_received'.encode('utf-8')
    msg.payload = json.dumps({'name': action_name}).encode('utf-8')

    func = mocker.stub('some_action_handler')

    connected_client.on_action(action_name, func)

    connected_client._on_action(None, None, msg)

    func.assert_called_once()


def test_should_not_use_action_handler_when_different_action_received(mocker, connected_client):
    action_name = 'some_action'
    other_action_name = 'other_action'

    msg = MQTTMessage()
    msg.topic = f'agent/{connected_client.client_id}/action_received'.encode('utf-8')
    msg.payload = json.dumps({'name': other_action_name}).encode('utf-8')

    func = mocker.stub('some_action_handler')

    connected_client.on_action(action_name, func)

    connected_client._on_action(None, None, msg)

    func.assert_not_called()


def test_should_use_any_action_handler_when_action_received(mocker, connected_client):
    action_name = 'some_action'

    msg = MQTTMessage()
    msg.topic = f'agent/{connected_client.client_id}/action_received'.encode('utf-8')
    msg.payload = json.dumps({'name': action_name}).encode('utf-8')

    func = mocker.stub('any_action_handler')

    connected_client.on_any_action(func)

    connected_client._on_action(None, None, msg)

    func.assert_called_once_with(action_name, [])


def test_should_use_action_handler_when_action_received_and_both_handlers_registered(mocker, connected_client):
    action_name = 'some_action'

    msg = MQTTMessage()
    msg.topic = f'agent/{connected_client.client_id}/action_received'.encode('utf-8')
    msg.payload = json.dumps({'name': action_name}).encode('utf-8')

    any_action_func = mocker.stub('any_action_handler')
    some_action_func = mocker.stub('some_action_handler')

    connected_client.on_any_action(any_action_func)
    connected_client.on_action(action_name, some_action_func)

    connected_client._on_action(None, None, msg)

    some_action_func.assert_called_once_with([])
    any_action_func.assert_not_called()


def test_on_any_action_should_accept_callback(connected_client):
    def func():
        pass

    connected_client.on_any_action(func)


def test_on_action_should_accept_specific_name_and_callback(connected_client):
    def handler():
        pass

    action_name = 'some_action_name'

    connected_client.on_action(action_name, handler)


@pytest.mark.parametrize("func", [
    None,
    {},
    123,
    '',
    [],
])
def test_on_any_action_should_raise_error_when_given_invalid_callback(func, connected_client):
    with pytest.raises(Exception):
        connected_client.on_any_action(func)


@pytest.mark.parametrize("action_name,func", [
    ('', None),
    ({}, lambda: None),
    ('', lambda: None),
    (123, 123),
    ('', ''),
    ([], []),
    (None, None),
    (None, lambda: 1),
])
def test_on_action_should_raise_error_when_given_invalid_name_or_callback(action_name, func, connected_client):
    with pytest.raises(Exception):
        connected_client.on_action(action_name, func)
