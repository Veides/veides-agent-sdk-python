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
        # Set DEBUG level to see received and sent data. Level is logging.WARN by default
        log_level=logging.DEBUG
    )

    client.connect()

    # Set a handler for particular action
    def on_set_low_speed_action(name, entities):
        client.send_trail('speed_level', 'low')
        client.send_action_completed(name)

    client.on_action('set_low_speed', on_set_low_speed_action)

    # You can also set a handler for any action received.
    # It will execute when there's no callback set for the particular action
    # def any_action_handler(name, entities):
    #     client.send_action_completed(name)

    # client.on_any_action(any_action_handler)

    # Set a handler for particular method
    def on_shutdown_method_invoked(name, payload):
        client.send_method_response(name, {"received_payload": payload})

    client.on_method('shutdown', on_shutdown_method_invoked)

    # You can also set a handler for any method invoked.
    # It will execute when there's no callback set for the particular method
    # def on_any_method_invoked(name, payload):
    #     client.send_method_response(name, {"received_payload": payload})

    # client.on_any_method(on_any_method_invoked)

    # Send initial facts
    client.send_facts({
        'battery_level': 'full',
        'charging': 'no',
    })

    # Send a trail
    client.send_trail('speed_level', 'normal')

    # Send ready event
    client.send_event('ready_to_rock')

    uptime = 0
    finish = False

    while not finish:
        try:
            sleep(1)
            uptime += 1

            # Send trail
            client.send_trail('uptime', uptime)

            if uptime == 10:
                # Send facts update
                client.send_facts({
                    'battery_level': 'low',
                })
        except KeyboardInterrupt:
            finish = True
            pass

    # Send facts update
    client.send_facts({
        'battery_level': 'unknown',
    })

    client.disconnect()
