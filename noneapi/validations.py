import inspect
from typing import Any, Callable, List

from pydantic import BaseModel


def validate_or_ignore(func: Callable, *args: List[Any], **kwargs: Any):
    """
    Validate the arguments of a function against the type hints of the
    function. If the arguments aren't valid, raise a Validation error.
    """
    inspected = inspect.getfullargspec(func)

    # Validate positional arguments
    for i, arg_value in enumerate(args):
        arg_name = inspected.args[i]
        arg_type = inspected.annotations.get(arg_name, None)

        if arg_type:
            validate_argument(arg_name, arg_value, arg_type)

    # Validate keyword arguments
    for arg_name, arg_value in kwargs.items():
        arg_type = inspected.annotations.get(arg_name, None)

        if arg_type:
            validate_argument(arg_name, arg_value, arg_type)


def validate_argument(arg_name: str, arg_value: Any, arg_type: type):
    """
    Validate a single argument.
    """

    if isinstance(arg_type, type) and issubclass(arg_type, BaseModel):
        arg_type(**arg_value)
    elif hasattr(arg_type, "__origin__"):
        if not isinstance(arg_value, arg_type.__origin__):
            raise ValueError(
                f"Argument {arg_name} should be of type {arg_type}"
            )
    else:
        if not isinstance(arg_value, arg_type):
            raise ValueError(
                f"Argument {arg_name} should be of type {arg_type}"
            )
