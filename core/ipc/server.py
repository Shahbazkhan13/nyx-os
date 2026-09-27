"""NyxOS IPC Server — Unix socket JSON-RPC style server."""
import os
import socket
import threading
import json
import traceback
from pathlib import Path

from core.ipc.protocol import make_message, encode, decode


DEFAULT_SOCKET = os.path.expanduser("~/.nyxos/nyxos.sock")


class IPCServer:
    def __init__(self, path=None, bus=None):
        self.path = path or DEFAULT_SOCKET
        self.bus = bus
        self.handlers = {}
        self._sock = None
        self._running = False
        self._thread = None

    def register(self, method, handler):
        """handler(params) -> result dict"""
        self.handlers[method] = handler

    def _handle_client(self, conn):
        try:
            buf = b""
            while True:
                data = conn.recv(4096)
                if not data:
                    break
                buf += data
                while b"\n" in buf:
                    line, buf = buf.split(b"\n", 1)
                    if not line.strip():
                        continue
                    try:
                        msg = decode(line)
                        resp = self._dispatch(msg)
                        conn.sendall(encode(resp))
                    except Exception as e:
                        err = make_message("error", error=str(e))
                        conn.sendall(encode(err))
        except Exception:
            traceback.print_exc()
        finally:
            conn.close()

    def _dispatch(self, msg):
        method = msg.get("method")
        params = msg.get("params", {})
        msg_id = msg.get("id")
        if method not in self.handlers:
            return make_message("error", msg_id=msg_id,
                                error=f"Unknown method: {method}")
        try:
            result = self.handlers[method](params)
            return make_message("response", msg_id=msg_id, result=result)
        except Exception as e:
            return make_message("error", msg_id=msg_id, error=str(e))

    def start(self):
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        if os.path.exists(self.path):
            os.unlink(self.path)
        self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._sock.bind(self.path)
        self._sock.listen(8)
        self._running = True
        self._thread = threading.Thread(target=self._accept_loop, daemon=True)
        self._thread.start()
        return self

    def _accept_loop(self):
        while self._running:
            try:
                conn, _ = self._sock.accept()
                t = threading.Thread(target=self._handle_client, args=(conn,), daemon=True)
                t.start()
            except OSError:
                break

    def stop(self):
        self._running = False
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass
        if os.path.exists(self.path):
            try:
                os.unlink(self.path)
            except Exception:
                pass
