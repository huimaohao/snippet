"""

``` Shell
pip install pydantic
```

"""

import inspect

from datetime import datetime
from pydantic import BaseModel, PositiveInt, ValidationError


def print_title(title, width=120, bgn="", end=""):
    print(bgn, end="")
    sub = width - len(title)
    sub_div_2 = sub // 2
    sub_mod_2 = sub % 2
    print("-" * (sub_div_2 - 1), title, "-" * (sub_div_2 + sub_mod_2 - 1))
    print(end, end="")


def demo__valid():
    func_name = inspect.currentframe().f_code.co_name
    print_title(func_name, bgn="\n", end="\n")

    class User(BaseModel):
        id: int
        name: str = "John Doe"
        signup_ts: datetime | None
        tastes: dict[str, PositiveInt]

    external_data = {
        "id": 123,
        "signup_ts": "2019-06-01 12:22",
        "tastes": {
            "wine": 9,
            b"cheese": 7,
            "cabbage": "1",
        },
    }

    user = User(**external_data)

    print(user.id)
    print(user.name)
    print(user.signup_ts)
    print(user.tastes)
    print()
    print(user.model_dump())
    print()
    print(user.model_dump_json(indent=2))


def demo__invalid():
    func_name = inspect.currentframe().f_code.co_name
    print_title(func_name, bgn="\n", end="\n")

    class User(BaseModel):
        id: int
        name: str = "John Doe"
        signup_ts: datetime | None
        tastes: dict[str, PositiveInt]

    external_data = {"id": "not an int", "tastes": {}}

    try:
        User(**external_data)
    except ValidationError as e:
        print(e)
        print()
        print(e.errors())


if __name__ == "__main__":
    demo__valid()
    demo__invalid()
