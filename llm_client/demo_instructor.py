"""

``` Shell
pip install instructor

pip install python-dotenv
```

"""

import functools
import inspect
import os

import instructor
from instructor import llm_validator

from dotenv import load_dotenv
from pydantic import BaseModel, BeforeValidator, ValidationError, Field, field_validator
from typing import Annotated, List

load_dotenv()


def print_title(title, width=120, bgn="", end=""):
    print(bgn, end="")
    sub = width - len(title)
    sub_div_2 = sub // 2
    sub_mod_2 = sub % 2
    print("-" * (sub_div_2 - 1), title, "-" * (sub_div_2 + sub_mod_2 - 1))
    print(end, end="")


def print_title_args_kwargs(title, *args, **kwargs):
    print(f"event: {title}:")
    print(f"args: {args}")
    print(f"kwargs: {kwargs}\n")


def gen_print_args_kwargs(title):
    return functools.partial(print_title_args_kwargs, title)


print_completion_kwargs = gen_print_args_kwargs("completion:kwargs")
print_completion_response = gen_print_args_kwargs("completion:response")
print_completion_error = gen_print_args_kwargs("completion:error")
print_completion_last_attempt = gen_print_args_kwargs("completion:last_attempt")
print_parse_error = gen_print_args_kwargs("parse:error")


def demo__simple_structure():
    func_name = inspect.currentframe().f_code.co_name
    print_title(func_name, bgn="\n", end="\n")

    class UserInfo(BaseModel):
        name: str
        age: int

    client = instructor.from_provider(
        "deepseek/deepseek-v4-flash",
        extra_body={"thinking": {"type": "disabled"}},
        api_key=os.getenv("DEEPSEEK_API_KEY"),
    )
    client.on("completion:kwargs", print_completion_kwargs)
    client.on("completion:response", print_completion_response)
    client.on("completion:error", print_completion_error)
    client.on("completion:last_attempt", print_completion_last_attempt)
    client.on("parse:error", print_parse_error)

    user_info = client.create(
        response_model=UserInfo,
        messages=[{"role": "user", "content": "John Doe is 30 years old."}],
    )
    print(user_info)


def demo__complex_structure():
    func_name = inspect.currentframe().f_code.co_name
    print_title(func_name, bgn="\n", end="\n")

    class Address(BaseModel):
        street: str
        city: str
        state: str
        zip_code: str

    class Person(BaseModel):
        name: str
        age: int
        addresses: List[Address]

    client = instructor.from_provider(
        "deepseek/deepseek-v4-flash",
        extra_body={"thinking": {"type": "disabled"}},
        api_key=os.getenv("DEEPSEEK_API_KEY"),
    )
    client.on("completion:kwargs", print_completion_kwargs)
    client.on("completion:response", print_completion_response)
    client.on("completion:error", print_completion_error)
    client.on("completion:last_attempt", print_completion_last_attempt)
    client.on("parse:error", print_parse_error)

    person = client.create(
        response_model=Person,
        messages=[
            {
                "role": "user",
                "content": "Extract: John Smith is 35 years old. He has homes at 123 Main St, Springfield, IL 62704 and 456 Oak Ave, Chicago, IL 60601.",
            }
        ],
    )
    print(person)


def demo__prompt_template():
    func_name = inspect.currentframe().f_code.co_name
    print_title(func_name, bgn="\n", end="\n")

    class User(BaseModel):
        name: str
        age: int

    client = instructor.from_provider(
        "deepseek/deepseek-v4-flash",
        extra_body={"thinking": {"type": "disabled"}},
        api_key=os.getenv("DEEPSEEK_API_KEY"),
    )
    client.on("completion:kwargs", print_completion_kwargs)
    client.on("completion:response", print_completion_response)
    client.on("completion:error", print_completion_error)
    client.on("completion:last_attempt", print_completion_last_attempt)
    client.on("parse:error", print_parse_error)

    user = client.create(
        messages=[
            {
                "role": "user",
                "content": "Extract the information from the following text: {{ data }}",
            }
        ],
        response_model=User,
        context={"data": "John Doe is thirty years old"},
    )
    print(user)


def demo__streaming_response():
    func_name = inspect.currentframe().f_code.co_name
    print_title(func_name, bgn="\n", end="\n")

    class Address(BaseModel):
        street: str
        city: str
        state: str
        zip_code: str

    class Person(BaseModel):
        name: str
        age: int
        addresses: List[Address]

    client = instructor.from_provider(
        "deepseek/deepseek-v4-flash",
        extra_body={"thinking": {"type": "disabled"}},
        api_key=os.getenv("DEEPSEEK_API_KEY"),
    )
    client.on("completion:kwargs", print_completion_kwargs)
    client.on("completion:response", print_completion_response)
    client.on("completion:error", print_completion_error)
    client.on("completion:last_attempt", print_completion_last_attempt)
    client.on("parse:error", print_parse_error)

    stream = client.create_partial(
        response_model=Person,
        messages=[
            {
                "role": "user",
                "content": "Extract a detailed person profile for John Smith, 35, who lives in Chicago and Springfield.",
            }
        ],
    )
    for partial in stream:
        print(partial)


def demo__model_validation():
    func_name = inspect.currentframe().f_code.co_name
    print_title(func_name, bgn="\n", end="\n")

    class User(BaseModel):
        name: str
        age: int = Field(gt=0, lt=120)  # Age must be between 0 and 120

        @field_validator("name")
        def name_must_have_space(cls, v):
            if " " not in v:
                raise ValueError("Name must include first and last name")
            return v

    client = instructor.from_provider(
        "deepseek/deepseek-v4-flash",
        extra_body={"thinking": {"type": "disabled"}},
        api_key=os.getenv("DEEPSEEK_API_KEY"),
    )
    client.on("completion:kwargs", print_completion_kwargs)
    client.on("completion:response", print_completion_response)
    client.on("completion:error", print_completion_error)
    client.on("completion:last_attempt", print_completion_last_attempt)
    client.on("parse:error", print_parse_error)

    user = client.create(
        response_model=User,
        messages=[{"role": "user", "content": "Extract: Tom is 25 years old."}],
    )
    print(user)


def demo__field_validation():
    func_name = inspect.currentframe().f_code.co_name
    print_title(func_name, bgn="\n", end="\n")

    client = instructor.from_provider(
        "deepseek/deepseek-v4-flash",
        extra_body={"thinking": {"type": "disabled"}},
        api_key=os.getenv("DEEPSEEK_API_KEY"),
    )
    client.on("completion:kwargs", print_completion_kwargs)
    client.on("completion:response", print_completion_response)
    client.on("completion:error", print_completion_error)
    client.on("completion:last_attempt", print_completion_last_attempt)
    client.on("parse:error", print_parse_error)

    class QuestionAnswer(BaseModel):
        question: str
        answer: Annotated[
            str,
            BeforeValidator(
                llm_validator(
                    "don't say objectionable things",
                    client=client,
                    model="deepseek-v4-flash",
                )
            ),
        ]

    try:
        qa = QuestionAnswer(
            question="What is the meaning of life?",
            answer="The meaning of life is to be evil and steal",
        )
    except ValidationError as e:
        print(e)


if __name__ == "__main__":
    demo__simple_structure()
    demo__complex_structure()

    demo__prompt_template()

    demo__streaming_response()

    demo__model_validation()
    demo__field_validation()
