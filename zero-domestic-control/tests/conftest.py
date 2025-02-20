import pathlib
import pytest


def pytest_addoption(parser):
    parser.addoption("--run", help="run unit or integration tests", default="unit")


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    rootdir = pathlib.Path(item.config.rootdir)
    run = item.config.getoption("run")
    rel_path = pathlib.Path(item.fspath)
    print(rel_path)
    if rel_path.is_relative_to(rootdir / "tests" / "integration") and run not in {
        "integration",
        "all",
    }:
        pytest.skip(f"skipping {item} because --run=integration was not specified")
    if rel_path.is_relative_to(rootdir / "tests" / "unit") and run not in {
        "unit",
        "all",
    }:
        pytest.skip(f"skipping {item} because --run=unit was not specified")
