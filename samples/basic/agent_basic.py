from veides.sdk.agent import AgentClient, ConnectionProperties, AgentProperties
from time import sleep
import logging
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Basic example of connecting agent to Veides")

    parser.add_argument("-i", "--client-id", required=True, help="Client id of agent")
    parser.add_argument("-k", "--key", required=True, help="Key of agent")
    parser.add_argument("-s", "--secret-key", required=True, help="Secret key of agent")
    parser.add_argument("-H", "--host", required=True, help="Host to connect to")

    args = parser.parse_args()

    client = AgentClient(
        connection_properties=ConnectionProperties(host=args.host),
        # If you want to provide connection properties in environment, use below line instead
        # connection_properties=ConnectionProperties.from_env()
        agent_properties=AgentProperties(
            client_id=args.client_id,
            key=args.key,
            secret_key=args.secret_key
        ),
        # If you want to provide agent properties in environment, use below line instead
        # agent_properties=AgentProperties.from_env()
        log_level=logging.INFO  # logging.WARN by default
    )

    client.connect()

    # set a handler for any action received
    # def any_action_handler(name, entities):
    #     client.send_action_completed(name)

    # client.on_any_action(any_action_handler)

    # set a handler for particular action
    # def slow_down_handler(entities):
    #     client.send_action_completed('slow_down')

    # client.on_action('slow_down', slow_down_handler)

    # send initial facts
    # client.send_facts({
    #     'battery_level': 'full'
    # })

    # send ready event
    # client.send_event('ready_to_rock')

    up_time = 0

    try:
        while True:
            # send example trail (to see the value you need to setup dashboard first)
            # client.send_trail('up_time', up_time)

            sleep(1)
            up_time += 1
    except KeyboardInterrupt:
        pass

    client.disconnect()
