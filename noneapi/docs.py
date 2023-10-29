import os
from pathlib import Path

from gevent import monkey  # type: ignore
from pdoc import pdoc, web

from .events import _REGISTERED_EVENT_HANDLERS
from .rpc import _REGISTERED_METHODS

monkey.patch_all()


__all__ = ("generate_docs_for_service", "start_docs_server")


def get_paths(service_name: str) -> list[Path]:
    rpc_paths = set()

    for key, method in _REGISTERED_METHODS.items():
        if service_name not in key:
            continue
        rpc_paths.add(Path(method.__code__.co_filename))  # type: ignore

    event_paths = set()

    for k, handler in _REGISTERED_EVENT_HANDLERS.items():
        if service_name not in k:
            continue

        event_paths.add(Path(handler.__code__.co_filename))  # type: ignore

    all_paths = rpc_paths.union(event_paths)
    list_all_paths = list(all_paths)

    return list_all_paths


def generate_docs_for_service(
    list_paths: list[Path], output_dir: Path | str | None = None
) -> None:
    """
    Generate documentation for the service.
    :param list_paths: list of paths to generate documentation for.
    :param output_dir: Output directory for the documentation.
    :return: None
    """
    if not output_dir:
        output_dir = os.path.join(os.getcwd(), ".docs")

    if isinstance(output_dir, str):
        output_dir = Path(output_dir)

    pdoc(*list_paths, output_directory=output_dir)


def start_docs_server(modules: list[str], host: str, port: int) -> None:
    """
    Start the documentation server.
    :param modules: List of modules to generate documentation for.
    :param host: Host to start the server on.
    :param port: Port to start the server on.
    :return: None
    """

    httpd = web.DocServer((host, port), modules)

    with httpd:
        httpd.serve_forever()
