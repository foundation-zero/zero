import jwt

from ..adapter.config import Settings

settings = Settings()

SUPPORTED_ROLES = {"captain", "engineer", "first_officer", "crew", "guest"}


async def generate_jwt(args):
    unique_roles = set(args.roles)
    roles = list(unique_roles)

    if unsupported_roles := (unique_roles - SUPPORTED_ROLES):
        raise ValueError(
            f"Roles {unsupported_roles} are not supported. Supported roles are: {', '.join(SUPPORTED_ROLES)}"
        )

    claims = {
        "x-hasura-default-role": "crew",
        "x-hasura-allowed-roles": roles,
    }

    token = jwt.encode(
        {"https://hasura.io/jwt/claims": claims},
        settings.jwt_secret,
        algorithm="HS256",
    )
    print(f"JWT for roles ({', '.join(roles)}): {token}")
