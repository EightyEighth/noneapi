import inspect
from typing import Any, Callable

from pydantic import BaseModel


def validate_or_ignore(func: Callable, *args: list[Any], **kwargs: Any):
    """
    Validate the arguments of a function against the type hints of the
    function. If the arguments aren't valid raise Validation error.
    :param func:  function to validate
    :param args: parameters of the function
    :return: None
    """
    inspected = inspect.getfullargspec(func)

    for i, _arg in enumerate(args):
        arg_name = inspected.args[i]
        arg_type = inspected.annotations.get(arg_name)

        if arg_type is None:
            continue

        if issubclass(arg_type, BaseModel):
            arg_type(**_arg)
            continue

        if not isinstance(_arg, arg_type):
            raise ValueError(
                f"Argument {arg_name} should be of type {arg_type}"
            )

    for arg_name, arg_type in inspected.annotations.items():
        if arg_name in kwargs:
            if issubclass(arg_type, BaseModel):
                arg_type(**kwargs[arg_name])
                continue

            if not isinstance(kwargs[arg_name], arg_type):
                raise ValueError(
                    f"Argument {arg_name} should be of type {arg_type}"
                )
