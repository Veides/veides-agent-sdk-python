import json
import logging
import paho.mqtt.client as paho

from veides.sdk.agent.base_client import BaseClient
from veides.sdk.agent.properties import AgentProperties, ConnectionProperties


class AgentClient(BaseClient):
    def __init__(
            self,
            agent_properties,
            connection_properties,
            logger=None,
            mqtt_logger=None,
            log_level=logging.WARN,
            mqtt_log_level=logging.ERROR
    ):
        """
        Extends BaseClient with Veides features

        :param agent_properties: Properties related to agent
        :type agent_properties: AgentProperties
        :param connection_properties: Properties related to Veides connection
        :type connection_properties: ConnectionProperties
        :param logger: Custom SDK logger
        :type logger: logging.Logger
        :param mqtt_logger: Custom MQTT lib logger
        :type mqtt_logger: logging.Logger
        :param log_level: SDK logging level
        :param mqtt_log_level: MQTT lib logging level
        :param capath: Path to certificates directory
        """
        BaseClient.__init__(
            self,
            client_id=agent_properties.client_id,
            key=agent_properties.key,
            secret_key=agent_properties.secret_key,
            host=connection_properties.host,
            capath=connection_properties.capath,
            logger=logger,
            mqtt_logger=mqtt_logger,
            log_level=log_level,
            mqtt_log_level=mqtt_log_level,
        )

        self._any_action_handler = None
        self._action_handlers = {}

        action_received_topic = 'agent/{}/action_received'.format(agent_properties.client_id)

        self.client.message_callback_add(action_received_topic, self._on_action)
        self._subscribed_topics[action_received_topic] = 1

    def on_any_action(self, func):
        """
        Register a callback for any action. It will execute when there's no
        callback set for the particular action (see on_action())

        :param func: Callback for actions
        :type func: callable
        :return void
        """
        if not callable(func):
            raise TypeError('callback should be callable')

        self._any_action_handler = func

    def on_action(self, name, func):
        """
        Register a callback for the particular action

        :param name: Expected action name
        :type name: str
        :param func: Callback for action
        :type func: callable
        :return void
        """
        if not isinstance(name, str):
            raise TypeError('action name should be a string')

        if len(name) == 0:
            raise ValueError('action name should be at least 1 length')

        if not callable(func):
            raise TypeError('callback should be callable')

        self._action_handlers[name] = func

    def send_action_completed(self, name):
        """
        Send action completed message

        :param name: Completed action name
        :type name: str
        :return bool
        """
        if not isinstance(name, str):
            raise TypeError('completed action name should be a string')

        if len(name) == 0:
            raise ValueError('completed action name should be at least 1 length')

        return self._publish(
            'agent/{}/action_completed'.format(self.client_id),
            {
                'name': name,
            }
        )

    def send_event(self, name):
        """
        Send an event

        :param name: Event name
        :type name: str
        :return bool
        """
        if not isinstance(name, str):
            raise TypeError('event name should be a string')

        if len(name) == 0:
            raise ValueError('event name should be at least 1 length')

        return self._publish(
            'agent/{}/event'.format(self.client_id),
            {
                'name': name,
            }
        )

    def send_facts(self, facts):
        """
        Send new fact(s) value(s)

        :param facts: Simple key-value dictionary containing fact name (key) and fact value (value)
        :type facts: dict
        :return bool
        """
        if not isinstance(facts, dict):
            raise TypeError('facts should be a dictionary')

        if not all(map(lambda v: isinstance(v, str), facts.values())):
            raise TypeError('facts should be key-value string pairs')

        if not all(map(lambda v: len(v) > 0, facts.keys())):
            raise ValueError('fact names should be at least 1 length')

        if not all(map(lambda v: len(v) > 0, facts.values())):
            raise ValueError('fact values should be at least 1 length')

        return self._publish(
            'agent/{}/facts'.format(self.client_id),
            facts
        )

    def send_trail(self, name, value):
        """
        Send a trail

        :param name: Trail name
        :type name: str
        :param value: Trail value
        :type value: str|int|float
        :return bool
        """
        if not isinstance(name, str):
            raise TypeError('trail name should be a string')

        if len(name) == 0:
            raise ValueError('trail name should be at least 1 length')

        if not isinstance(value, str) and not isinstance(value, int) and not isinstance(value, float):
            raise TypeError('value name should be a string or number')

        if isinstance(value, str) and len(value) == 0:
            raise ValueError('value name should be at least 1 length')

        return self._publish(
            'agent/{}/trail/{}'.format(self.client_id, name),
            {
                'value': value,
            }
        )

    def _on_action(self, client, userdata, msg):
        """
        Dispatches received action to appropriate handler

        :param client: Paho client instance
        :type client: paho.Client
        :param userdata: User-defined data
        :type: userdata: object
        :param msg: Received Paho message
        :type msg: paho.MQTTMessage
        :return void
        """
        payload = json.loads(msg.payload)

        func = self._action_handlers.get(payload.get('name'), None)

        if func is not None:
            func(payload.get('entities', []))
        elif callable(self._any_action_handler):
            self._any_action_handler(payload.get('name'), payload.get('entities', []))
