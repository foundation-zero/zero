import jwt

from loads.config import Settings

SUPPORTED_ROLES = {"captain", "engineer", "first_officer", "crew", "guest"}


async def generate_jwt(settings: Settings, *_args, roles: str, jwt_secret: str):
    unique_roles = set(roles.split(","))
    roles_list = list(unique_roles)

    if unsupported_roles := (unique_roles - SUPPORTED_ROLES):
        raise ValueError(
            f"Roles {unsupported_roles} are not supported. Supported roles are: {', '.join(SUPPORTED_ROLES)}"
        )

    claims = {
        "x-hasura-default-role": "crew",
        "x-hasura-allowed-roles": roles_list,
    }

    token = jwt.encode(
        {"https://hasura.io/jwt/claims": claims},
        jwt_secret,
        algorithm="HS256",
    )
    print(f"JWT for roles ({', '.join(roles_list)}): {token}")
