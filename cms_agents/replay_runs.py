import argparse

from bluesky_kafka import Publisher
from nslsii.kafka_utils import _read_bluesky_kafka_config_file
from tiled.client import from_profile


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--produce",
        default=False,
        action="store_true", help="set to produce Kafka messsages"
    )

    return parser.parse_args()


def replay_runs(produce):
    kafka_config = _read_bluesky_kafka_config_file("/etc/bluesky/kafka.yml")
    bluesky_document_producer = Publisher(
        topic="cms.test",
        bootstrap_servers=",".join(kafka_config["bootstrap_servers"]),
        key="cms-pta-replay-scans",
        producer_config=kafka_config["runengine_producer_config"],
    )

    cms_client = from_profile("cms")

    print()
    if produce:
        print("replaying runs to topic cms.test")
    else:
        print("Kafka messages will not be produced because --produce was not specified on the command line")
    print()
    print("enter lists of space-separated scan ids to be replayed")
    print("enter an empty list to quit")
    print()
    while True:
        try:
            scan_ids_input = input("scan ids to replay: ")
            scan_ids = scan_ids_input.split()
            if len(scan_ids) == 0:
                print("all done!")
                break
            else:
                for scan_id in scan_ids:
                    print(f"replaying scan id {scan_id}")
                    if produce:
                        for name, document in cms_client[int(scan_id)].documents():
                            print(f"  producing message with {name} document")
                            bluesky_document_producer(name, document)
                        bluesky_document_producer.flush()
                    else:
                        print("  no messages produced")
        except KeyboardInterrupt:
            print()
            print("all done!")
            break


if __name__ == "__main__":
    replay_run_args = get_args()
    replay_runs(**vars(replay_run_args))
