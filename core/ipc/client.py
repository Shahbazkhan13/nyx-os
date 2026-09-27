"""NyxOS IPC Client — talk to IPC server."""
import socket
import os
from core.ipc.protocol import encode, decode, make_message

DEFAULT_SOCKET = os.path.expanduser("~/.nyxos/nyxos.sock")


class IPCClient:
    def __init__(self, path=None):
        self.path = path or DEFAULT_SOCKET

    def call(self, method, params=None):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            sock.connect(self.path)
            msg = make_message("request", method=method, params=params or {})
            sock.sendall(encode(msg))
            data = b""
            while b"\n" not in data:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                data += chunk
            resp = decode(data.split(b"\n")[0])
            if resp.get("type") == "error":
                raise RuntimeError(resp.get("error"))
            return resp.get("result")
        finally:
            sock.close()
