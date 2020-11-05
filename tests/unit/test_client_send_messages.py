import pytest
import json
from tests.unit.fixtures import (
    connected_client,
    mocked_paho_client,
    agent_key,
    agent_secret_key,
    hostname
)


def test_should_send_action_completed_without_facts(connected_client):
    action_name = 'some_action_name'

    connected_client.send_action_completed(action_name)

    connected_client.client.publish.assert_called_once_with(
        'agent/{}/action_completed'.format(connected_client.client_id),
        json.dumps({
            'name': action_name,
        }),
        qos=1,
        retain=False
    )


@pytest.mark.parametrize("action_name", [
    None,
    {},
    123,
    '',
])
def test_should_raise_error_if_given_invalid_action_completed_name(action_name, connected_client):
    with pytest.raises(Exception):
        connected_client.send_action_completed(action_name)


def test_should_send_event(connected_client):
    event_name = 'some_event_name'

    connected_client.send_event(event_name)

    connected_client.client.publish.assert_called_once_with(
        'agent/{}/event'.format(connected_client.client_id),
        json.dumps(dict(name=event_name)),
        qos=1,
        retain=False
    )


@pytest.mark.parametrize("event_name", [
    None,
    {},
    123,
])
def test_should_raise_error_if_given_invalid_event_name(event_name, connected_client):
    with pytest.raises(Exception):
        connected_client.send_event(event_name)


def test_should_send_facts(connected_client):
    facts = {
        'some_fact_name': 'some_fact_value'
    }

    connected_client.send_facts(facts)

    connected_client.client.publish.assert_called_once_with(
        'agent/{}/facts'.format(connected_client.client_id),
        json.dumps(facts),
        qos=1,
        retain=False
    )


@pytest.mark.parametrize("facts", [
    [],
    'string',
    123,
    {'name': {}},
    {'name': 'value', 'other_name': {}},
    {'': ''},
    {'name': ''},
])
def test_should_raise_error_if_given_invalid_facts(facts, connected_client):
    with pytest.raises(Exception):
        connected_client.send_facts(facts)
