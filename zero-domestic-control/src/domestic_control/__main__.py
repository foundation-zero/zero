from argparse import ArgumentParser
import asyncio

import jwt

from domestic_control.config import Settings
import logging
from .logging import setup_logging
import uvicorn

setup_logging()

settings = Settings()  # type: ignore


async def run():
    parser = ArgumentParser("zero_domestic_control")
    sub_parser = parser.add_subparsers()

    generate_jwt_cmd = sub_parser.add_parser("generate-jwt")
    generate_jwt_cmd.add_argument("roles", type=str, nargs="*", help="any additional roles to generate jwt for")
    generate_jwt_cmd.add_argument("--cabin", type=str, help="specify the cabin for the JWT")

    generate_jwt_cmd.set_defaults(func=generate_jwt)

    control_cmd = sub_parser.add_parser("control")
    control_cmd.set_defaults(func=control)

    stub_cmd = sub_parser.add_parser("stub")
    stub_cmd.set_defaults(func=stub)

    api_cmd = sub_parser.add_parser("api")
    api_cmd.set_defaults(func=run_app)

    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
    else:
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
        {"https://hasura.io/jwt/claims": claims},
        settings.jwt_secret,
        algorithm="HS256",
    )
    print(f"JWT for roles ({', '.join(roles)}): {token}")


def run_app(_args):
    logging.info("Running API...")
    uvicorn.run("domestic_control.app:app", host="0.0.0.0", port=4001, reload=True)


async def control(_args):
    from domestic_control.control import Control

    async with Control.init_from_settings(settings) as control:
        logging.info("Running control...")
        await control.run()


async def stub(_args):
    from domestic_control.services.stubs import Stub

    async with Stub.from_settings(settings) as stub:
        logging.info("Running stub...")
        await stub.run()


def main():
    asyncio.run(run())


if __name__ == "__main__":
    main()
