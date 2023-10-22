import msgpack
import zmq
from loguru import logger


def debug(msg_or_socket: zmq.Socket | list[bytes]) -> list[bytes]:
    """Receives all message parts from socket, printing each frame neatly"""
    if isinstance(msg_or_socket, zmq.Socket):
        # it's a socket, call on current message
        msg = msg_or_socket.recv_multipart()
    else:
        msg = msg_or_socket
    logger.debug("----------------------------------------")
    for i, part in enumerate(msg):
        _len = len(part)
        try:
            logger.debug(f"Frame{i}[{_len}]: {msgpack.unpackb(part)}")
        except Exception:
            logger.debug(f"Frame{i}[{_len}]: {part.decode()}")

    return msg
