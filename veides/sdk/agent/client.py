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
        self._any_method_handler = None
        self._method_handlers = {}

        action_received_topic = 'agent/{}/action_received'.format(agent_properties.client_id)
        method_called_topic = 'agent/{}/method/+'.format(agent_properties.client_id)

        self.client.message_callback_add(action_received_topic, self._on_action)
        self.client.message_callback_add(method_called_topic, self._on_method)
        self._subscribed_topics[action_received_topic] = 1
        self._subscribed_topics[method_called_topic] = 1

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

    def on_any_method(self, func):
        """
        Register a callback for any method. It will execute when there's no
        callback set for the particular method (see on_method())

        :param func: Callback for methods
        :type func: callable
        :return void
        """
        if not callable(func):
            raise TypeError('callback should be callable')

        self._any_method_handler = func

    def on_method(self, name, func):
        """
        Register a callback for the particular method

        :param name: Expected method name
        :type name: str
        :param func: Callback for method
        :type func: callable
        :return void
        """
        if not isinstance(name, str):
            raise TypeError('method name should be a string')

        if len(name) == 0:
            raise ValueError('method name should be at least 1 length')

        if not callable(func):
            raise TypeError('callback should be callable')

        self._method_handlers[name] = func

    def send_method_response(self, name, payload, code=200):
        """
        Send the response to invoked method

        :param name: Method name
        :type name: str
        :param payload: A dictionary containing response to the method
        :type payload: dict|list|str|int|float|bool
        :param code: HTTP response code
        :type code: int
        :return bool
        """
        if not isinstance(name, str):
            raise TypeError('method name should be a string')

        if len(name) == 0:
            raise ValueError('method name should be at least 1 length')

        if payload is None:
            raise TypeError('body is required')

        if not isinstance(code, int):
            raise TypeError('code should be an integer')

        return self._publish(
            'agent/{}/method_response/{}'.format(self.client_id, name),
            {
                "payload": payload,
                "code": code
            }
        )

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

        if func is None and callable(self._any_action_handler):
            func = self._any_action_handler

        if func is not None:
            func(payload.get('name'), payload.get('entities', []))

    def _on_method(self, client, userdata, msg):
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
        method_name = msg.topic.split('/')[-1]
        payload = json.loads(msg.payload)

        func = self._method_handlers.get(method_name, None)

        if func is None and callable(self._any_method_handler):
            func = self._any_method_handler

        if func is not None:
            func(method_name, payload)
