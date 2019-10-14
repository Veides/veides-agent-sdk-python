import pytest
import json
from tests.unit.fixtures import connected_client
from paho.mqtt.client import MQTTMessage


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
