"""Fixtures shared by the cross-API suites: the running docker stack."""

import shutil
import subprocess

import pytest

from tests.graphql.stack_config import REPO_ROOT, STACK_SERVICES


@pytest.fixture(scope="session")
def docker_stack() -> None:
    """Ensure the services the suites talk to are up.

    If docker is unavailable in the current environment, the stack is assumed
    to already be running (e.g. started manually before invoking pytest) and
    this fixture is a no-op. Only ``STACK_SERVICES`` are waited on: grafana
    (profile ``data``) has a broken healthcheck (probes port 3001 but serves on
    3000) and would never become healthy, so it is deliberately not listed.
    """
    docker = shutil.which("docker")
    if docker is None:
        return
    subprocess.run(  # noqa: S603 - fixed argv, no user input
        [
            docker,
            "compose",
            "--profile",
            "thrs",
            "--profile",
            "data",
            "up",
            "-d",
            "--wait",
            *STACK_SERVICES,
        ],
        cwd=REPO_ROOT,
        check=True,
        timeout=300,
    )
