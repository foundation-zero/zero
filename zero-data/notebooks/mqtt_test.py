import argparse
import asyncio
from datetime import datetime
import aiomqtt

TEST_TOPIC = "robustness_test_topic"
RECONNECT_INTERVAL = 0.1
"""
Test script that allows to test robustness of the mqtt client.
Run two instances of the script with producer and consumer modes.
Then kill broker pods, or k8s nodes to see the impact on the clients.

Get mqtt broker that client is connected to:
vmq-admin session show --client_id --node --topic --topic=robustness_test_topic
"""


async def producer(host: str, port: int):
    message_number = 0
    client = aiomqtt.Client(host, port=port, identifier="test_client_producer")
    disconnected_time = None
    while True:
        try:
            async with client:
                while True:
                    await client.publish(TEST_TOPIC, payload=message_number, qos=2)
                    print(f"Published #{message_number}")
                    if disconnected_time is not None:
                        print(f"Reconnected after {datetime.now() - disconnected_time}")
                        disconnected_time = None
                    message_number += 1

                    await asyncio.sleep(1)
        except aiomqtt.MqttError:
            disconnected_time = datetime.now()
            await asyncio.sleep(RECONNECT_INTERVAL)


async def consumer(host: str, port: int):
    message_number = None
    client = aiomqtt.Client(
        host, port=port, clean_session=False, identifier="test_client_consumer"
    )
    disconnected_time = None
    async with client:
        await client.subscribe(TEST_TOPIC, qos=2)
    while True:
        try:
            async with client:
                async for message in client.messages:
                    if disconnected_time is not None:
                        print(f"Reconnected after {datetime.now() - disconnected_time}")
                        disconnected_time = None
                    this_number = int(message.payload)
                    if message_number is None or message_number + 1 == this_number:
                        print(f"Received and matched #{this_number}")
                        message_number = this_number
                    else:
                        print(
                            f"-------Message missed: Expected: {message_number + 1} Got: {str(message.payload)}"
                        )
                        message_number = this_number
        except aiomqtt.MqttError:
            disconnected_time = datetime.now()
            await asyncio.sleep(RECONNECT_INTERVAL)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", type=str, choices=["producer", "consumer"])
    parser.add_argument("--host", type=str, default="localhost")
    parser.add_argument("--port", type=int, default=1883)
    return parser.parse_args()


async def main():
    args = parse_args()
    if args.mode == "producer":
        await producer(args.host, args.port)
    elif args.mode == "consumer":
        await consumer(args.host, args.port)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
