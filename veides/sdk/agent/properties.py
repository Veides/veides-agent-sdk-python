import os
from veides.sdk.exceptions import ConfigurationException


class AgentProperties:
    def __init__(self, client_id, key, secret_key):
        """
        :param client_id: Agent's client id
        :type client_id: str
        :param key: Agent's key
        :type key: str
        :param secret_key: Agent's secret key
        :type secret_key: str
        """
        self._client_id = client_id
        self._key = key
        self._secret_key = secret_key

    @property
    def client_id(self):
        return self._client_id

    @property
    def key(self):
        return self._key

    @property
    def secret_key(self):
        return self._secret_key

    @staticmethod
    def from_env():
        """
        Returns AgentProperties instance built from env variables. Required variables are:
            1. VEIDES_AGENT_CLIENT_ID: agent's client id
            2. VEIDES_AGENT_KEY: agent's key
            3. VEIDES_AGENT_SECRET_KEY: agent's secret key

        :raises ConfigurationException: If required variables are not provided
        :return AgentProperties
        """
        client_id = os.getenv('VEIDES_AGENT_CLIENT_ID', None)
        key = os.getenv('VEIDES_AGENT_KEY', None)
        secret_key = os.getenv('VEIDES_AGENT_SECRET_KEY', None)

        if client_id is None:
            raise ConfigurationException("Missing 'VEIDES_AGENT_CLIENT_ID' variable in env")

        if key is None:
            raise ConfigurationException("Missing 'VEIDES_AGENT_KEY' variable in env")

        if secret_key is None:
            raise ConfigurationException("Missing 'VEIDES_AGENT_SECRET_KEY' variable in env")

        return AgentProperties(
            client_id=client_id,
            key=key,
            secret_key=secret_key
        )


class ConnectionProperties:
    def __init__(self, host, capath="/etc/ssl/certs"):
        """
        :param host: Hostname used to connect to Veides
        :type host: str
        :param capath: Path to certificates directory
        :type capath: str
        """
        self._host = host
        self._capath = capath

    @property
    def host(self):
        return self._host

    @property
    def capath(self):
        return self._capath

    @staticmethod
    def from_env():
        """
        Returns ConnectionProperties instance built from env variables. Required variables are:
            1. VEIDES_CLIENT_HOST: Hostname used to connect to Veides

        :raises ConfigurationException: If required variables are not provided
        :return ConnectionProperties
        """
        host = os.getenv('VEIDES_CLIENT_HOST', None)
        capath = os.getenv('VEIDES_CLIENT_CAPATH', "/etc/ssl/certs")

        if host is None:
            raise ConfigurationException("Missing 'VEIDES_CLIENT_HOST' variable in env")

        return ConnectionProperties(host, capath)
