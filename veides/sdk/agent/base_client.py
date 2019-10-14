import json
import socket
import ssl
import logging
import threading
import paho.mqtt.client as paho

from veides.sdk.exceptions import ConnectionException


class BaseClient(object):
    def __init__(
        self,
        client_id,
        key,
        secret_key,
        host,
        capath=None,
        log_level=logging.WARN,
        logger=None,
    ):
        """
        Underlying client implementation featuring Veides communication over MQTT

        :param client_id: Agent's client id. It may be obtained in console.
        :param key: Agent's key generated on adding agent. When lost new one can be obtained in console.
        :param secret_key: Agent's secret key generated on adding agent. When lost new one can be obtained in console.
        :param host:
        :param capath:
        :param log_level:
        :param logger:
        """
        self.client_id = client_id
        self.key = key
        self.secret_key = secret_key
        self.host = host

        self.connected = threading.Event()

        self._subscribed_topics = {}

        if logger is None:
            self.logger = logging.getLogger(self.__module__ + "." + self.__class__.__name__)
            self.logger.handlers = []
            self.logger.setLevel(log_level)

            handler = logging.StreamHandler()
            handler.setFormatter(
                logging.Formatter("%(asctime)s %(name)s [%(levelname)s] %(message)s")
            )

            self.logger.addHandler(handler)
        else:
            self.logger = logger

        self.client = paho.Client(self.client_id, transport="tcp", clean_session=True)
        
        self.client.username_pw_set(self.key, self.secret_key)

        try:
            self.client.tls_set_context(ssl.create_default_context(capath=capath))
            self.port = 8883
        except Exception as e:
            self.port = 1883
            self.logger.warning("Unable to use SSL/TLS: %s" % str(e))

        self.client.on_log = self._on_log
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect

    def connect(self):
        """
        :raises ConnectionException: If there's any connection problem
        """
        self.logger.debug("Connecting to %s:%d with client_id %s" % (self.host, self.port, self.client_id))
        
        try:
            self.connected.clear()
            self.client.connect(self.host, port=self.port, keepalive=60)
            self.client.loop_start()

            if not self.connected.wait(timeout=30):
                self.client.loop_stop()
                raise ConnectionException("Timeout occurred while connecting to Veides: %s" % self.host)

        except socket.error as e:
            self.client.loop_stop()
            raise ConnectionException("Failed to connect to Veides: %s" % str(e))

    def disconnect(self):
        self.logger.info("Closing connection to Veides")
        self.client.disconnect()
        self.client.loop_stop()
        self.logger.info("Closed connection to Veides")

    def is_connected(self):
        return self.connected.isSet()

    def _publish(self, topic, data, qos=1):
        """
        :param topic: Topic to publish message to
        :type topic: str
        :param data
        :type data: dict
        :param qos
        :type qos: int
        :return bool
        """
        if not self.connected.wait(timeout=10):
            self.logger.warning("Could not send message in disconnected state")
            return False

        self.logger.debug("Sending message to %s with data %s" % (topic, str(data)))

        payload = json.dumps(data)

        result = self.client.publish(topic, payload, qos=qos, retain=False)

        if result[0] == paho.MQTT_ERR_ACL_DENIED:
            self.logger.warning("No permission to send message on %s" % topic)
            return False

        return result[0] == paho.MQTT_ERR_SUCCESS

    def _on_log(self, client, userdata, level, string):
        """
        :param client: Paho client instance
        :type client: paho.Client
        :param userdata: User-defined data
        :type: userdata: object
        :param level: Severity level of message
        :type level: int
        :param string: The message
        :type string: str
        :return void
        """
        self.logger.log(paho.LOGGING_LEVEL[level], string)

    def _on_connect(self, client, userdata, flags, rc):
        """
        :param client: Paho client instance
        :type client: paho.Client
        :param userdata: User-defined data
        :type userdata: object
        :param flags: Response flags
        :type flags: dict
        :param rc: Connection response code
        :type rc: int
        :raises ConnectionException: If there's any connection problem
        :return void
        """
        if rc == 0:
            self.connected.set()
            self.logger.info("Connected successfully: %s" % self.client_id)

            if len(self._subscribed_topics) > 0:
                for subscription in self._subscribed_topics:
                    (result, mid) = self.client.subscribe(subscription, qos=self._subscribed_topics[subscription])
                    if result != paho.MQTT_ERR_SUCCESS:
                        raise ConnectionException("Unable to subscribe to %s" % subscription)
        elif rc == 1:
            raise ConnectionException("Unacceptable protocol version")
        elif rc == 2:
            raise ConnectionException("Identifier rejected")
        elif rc == 3:
            raise ConnectionException("Server unavailable")
        elif rc == 4:
            raise ConnectionException("Bad key or secret key")
        elif rc == 5:
            raise ConnectionException("Agent not authorized")
        else:
            raise ConnectionException("Connection failed with unknown reason. (rc=%d)" % rc)

    def _on_disconnect(self, client, userdata, rc):
        """
        :param client: Paho client instance
        :type client: paho.Client
        :param userdata: User-defined data
        :type: userdata: object
        :param rc: Disconnection state. Value different than `0` means that connection closed unexepected
        :type rc: int
        :return void
        """
        self.connected.clear()

        if rc != 0:
            self.logger.error("Unexpected disconnection from Veides: %d" % rc)
        else:
            self.logger.info("Disconnected from Veides")
