"""CLI entrypoint for zero-atpx-nmea.

Defaults to the original ``run`` action (start the FastStream MQTT bridge).
With the ``asyncapi`` action, prints the AsyncAPI 3.0.0 specification to stdout.
"""

import argparse
import json
import logging
import sys

from zero_atpx_nmea.app import build_app
from zero_atpx_nmea.asyncapi_spec import build_spec

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s"
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Zero ATPX NMEA: bridge A+T's NMEA 0183 stream to our MQTT broker"
    )
    parser.add_argument(
        "action",
        nargs="?",
        default="run",
        choices=("run", "asyncapi"),
        help="'run' (default) starts the MQTT bridge; 'asyncapi' prints the AsyncAPI spec to stdout",
    )
    args = parser.parse_args()

    if args.action == "asyncapi":
        spec = build_spec()
        json.dump(spec, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return

    app = build_app()
    try:
        import asyncio  # noqa: PLC0415

        asyncio.run(app.run())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
