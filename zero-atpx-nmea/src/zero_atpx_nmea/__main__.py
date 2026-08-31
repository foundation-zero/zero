import asyncio
import logging

from zero_atpx_nmea.app import build_app

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s"
)


def main() -> None:
    app = build_app()
    try:
        asyncio.run(app.run())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
