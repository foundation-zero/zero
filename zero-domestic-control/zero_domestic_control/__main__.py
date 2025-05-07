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
    generate_jwt_cmd.add_argument(
        "roles", type=str, nargs="*", help="any additional roles to generate jwt for"
    )
    generate_jwt_cmd.add_argument(
        "--cabin", type=str, help="specify the cabin for the JWT"
    )

    generate_jwt_cmd.set_defaults(func=generate_jwt)

    control_cmd = sub_parser.add_parser("control")
    control_cmd.set_defaults(func=control)

    stub_cmd = sub_parser.add_parser("stub")
    stub_cmd.set_defaults(func=stub)

    args = parser.parse_args()

    await args.func(args)


SUPPORTED_ROLES = {"user", "admin"}


async def generate_jwt(args):
    unique_roles = set(["user"] + args.roles)
    roles = list(unique_roles)

    if unsupported_roles := (unique_roles - SUPPORTED_ROLES):
        raise ValueError(
            f"Roles {unsupported_roles} are not supported. Supported roles are: {', '.join(SUPPORTED_ROLES)}"
        )
    
    claims = {
        "x-hasura-default-role": "user",
        "x-hasura-allowed-roles": roles,
    }
    
    if args.cabin:
        claims["x-hasura-cabin"] = args.cabin

    token = jwt.encode(
        {
            "https://hasura.io/jwt/claims": claims
        },
        settings.jwt_secret,
        algorithm="HS256",
    )
    print(f"JWT for roles ({", ".join(roles)}): {token}")


async def setup(_args):
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


async def control(_args):
    from zero_domestic_control.control import Control

    async with Control.init_from_settings(settings) as control:
        print("Running control")
        await control.run()


async def stub(_args):
    from zero_domestic_control.services.stubs import Stub

    async with Stub.from_settings(settings) as stub:
        print("Running stub")
        await stub.run()


if __name__ == "__main__":
    asyncio.run(run())
