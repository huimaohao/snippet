"""

``` Shell
pip install python-dotenv
```

"""

import os
import io
import inspect

from dotenv import load_dotenv, dotenv_values


def demo__load_dotenv():
    env_path = ".env"

    if os.path.exists(env_path):
        print("skip", inspect.currentframe().f_code.co_name)
        return

    with open(env_path, "w") as f:
        f.write("# Development settings\n")
        f.write("DOMAIN=example.org\n")
        f.write("ADMIN_EMAIL=admin@${DOMAIN}\n")
        f.write("ROOT_URL=${DOMAIN}/app\n")

    assert os.getenv("DOMAIN") == None
    assert os.getenv("ADMIN_EMAIL") == None
    assert os.getenv("ROOT_URL") == None

    load_dotenv()

    assert os.getenv("DOMAIN") == "example.org"
    assert os.getenv("ADMIN_EMAIL") == "admin@example.org"
    assert os.getenv("ROOT_URL") == "example.org/app"

    os.remove(env_path)


def demo__dotenv_values():
    env_path = ".env"

    if os.path.exists(env_path):
        print("skip", inspect.currentframe().f_code.co_name)
        return

    with open(env_path, "w") as f:
        f.write("USER=foo\n")
        f.write("EMAIL=${USER}@${DOMAIN}\n")

    config = dotenv_values(env_path)

    assert os.getenv("USER") == None
    assert os.getenv("EMAIL") == None
    assert config["USER"] == "foo"
    assert config["EMAIL"] == "foo@example.org"

    os.remove(env_path)


def demo__dotenv_values__merge():
    env_shared_path = ".env.shared"
    env_secret_path = ".env.secret"

    if os.path.exists(env_shared_path) or os.path.exists(env_secret_path):
        print("skip", inspect.currentframe().f_code.co_name)
        return

    with open(env_shared_path, "w") as f:
        f.write("ADMIN_EMAIL=shared_admin@example.org\n")
        f.write("SHARED_EMAIL=shared@example.org\n")

    with open(env_secret_path, "w") as f:
        f.write("ADMIN_EMAIL=secret_admin@example.org\n")
        f.write("SECRET_EMAIL=secret@example.org\n")

    config = {
        **dotenv_values(".env.shared"),
        **dotenv_values(".env.secret"),
        **os.environ,
    }

    assert config["ADMIN_EMAIL"] == "admin@example.org"
    assert config["SHARED_EMAIL"] == "shared@example.org"
    assert config["SECRET_EMAIL"] == "secret@example.org"

    os.remove(env_shared_path)
    os.remove(env_secret_path)


def demo__load_dotenv__stream():
    config = io.StringIO("USER=foo\nEMAIL=foo@example.org")

    assert os.getenv("USER") == None
    assert os.getenv("EMAIL") == None

    load_dotenv(stream=config)

    assert os.getenv("USER") == "foo"
    assert os.getenv("EMAIL") == "foo@example.org"


if __name__ == "__main__":
    # order matters
    demo__load_dotenv()
    demo__dotenv_values()
    demo__dotenv_values__merge()
    demo__load_dotenv__stream()
