import pytest
import os

# Import the fuctional fixtures as a plugin
# Note: fixtures with session scope need to be local
pytest_plugins = ["dbt.tests.fixtures.project"]


def pytest_addoption(parser):
    parser.addoption("--profile", action="store", default="analyticdb", type=str)


# Using @pytest.mark.skip_profile uses the 'skip_by_profile_type'
# autouse fixture below
def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "skip_profile(profile): skip test for the given profile",
    )


# The profile dictionary, used to write out profiles.yml
@pytest.fixture(scope="session")
def dbt_profile_target(request):
    profile_type = request.config.getoption("--profile")
    if profile_type == "analyticdb":
        target = analyticdb_target()
    else:
        raise ValueError(f"Invalid profile type '{profile_type}'")
    return target


# dbt will supply a unique schema per test, so we do not specify 'schema' here
def analyticdb_target():
    return {
        "type": "analyticdb",
        "port": int(os.getenv("DBT_MYSQL_80_PORT", "3306")),
        "server": os.getenv("DBT_MYSQL_SERVER_NAME", "localhost"),
        "username": os.getenv("DBT_MYSQL_USERNAME", "root"),
        "password": os.getenv("DBT_MYSQL_PASSWORD", "dbt"),
    }


@pytest.fixture(autouse=True)
def skip_by_profile_type(request):
    profile_type = request.config.getoption("--profile")
    if request.node.get_closest_marker("skip_profile"):
        for skip_profile_type in request.node.get_closest_marker("skip_profile").args:
            if skip_profile_type == profile_type:
                pytest.skip(f"skipped on '{profile_type}' profile")
