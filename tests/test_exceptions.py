from noneapi.exceptions import RemoteError
from noneapi.handlers import RemoteErrorHandler


def test_remote_error_to_dict():
    error = RemoteError(
        original_exc=Exception("Test"),
        message="Test"
    )

    assert error.to_dict() == {
        'exc_type': 'Exception',
        'exc_path': 'builtins.Exception',
        'exc_args': ['Test'],
        'value': 'Test'
    }


def test_remote_error_from_dict():
    error = RemoteError(
        original_exc=Exception("Test"),
        message="Test"
    )

    error_dict = error.to_dict()

    new_error = RemoteError.from_dict(error_dict)

    assert isinstance(new_error, Exception)
    assert ("Test", ) == error._original_exc.args


def test_error_handler():
    error = RemoteError(
        original_exc=Exception("Test"),
        message="Test"
    )

    handler = RemoteErrorHandler()

    assert isinstance(handler.handle_exception(error), dict)
