from argparse import ArgumentParser
import asyncio
import codecs

import jwt
import psycopg

from zero_domestic_control.config import Settings

settings = Settings()


async def run():
    parser = ArgumentParser("zero_domestic_control")
    sub_parser = parser.add_subparsers()

    setup_cmd = sub_parser.add_parser("setup")
    setup_cmd.set_defaults(func=setup)

    generate_jwt_cmd = sub_parser.add_parser("generate-jwt")
    generate_jwt_cmd.set_defaults(func=generate_jwt)

    await parser.parse_args().func()


async def generate_jwt():
    token = jwt.encode(
        {
            "https://hasura.io/jwt/claims": {
                "x-hasura-default-role": "user",
                "x-hasura-allowed-roles": ["user"],
            }
        },
        settings.jwt_secret,
        algorithm="HS256",
    )
    print(f"JWT: {token}")


async def setup():
    print("Setting up postgres")
    async with await psycopg.AsyncConnection.connect(settings.pg_url) as conn:
        async with conn.cursor() as cur:
            with codecs.open(
                "./zero_domestic_control/postgres.sql", encoding="utf-8"
            ) as query:
                await cur.execute(bytes(query.read(), "utf-8"))

    print("Setting up risingwave")
    async with await psycopg.AsyncConnection.connect(settings.risingwave_url) as conn:
        async with conn.cursor() as cur:
            with codecs.open(
                "./zero_domestic_control/risingwave.sql", encoding="utf-8"
            ) as query:
                await cur.execute(bytes(query.read(), "utf-8"))


if __name__ == "__main__":
    asyncio.run(run())
