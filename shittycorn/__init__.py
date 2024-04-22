import io
import logging
import signal
import socket
from wsgiref.types import WSGIApplication


logger = logging.getLogger("shittycorn")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)


class Server:
    def __init__(self, host: str, port: int, app: WSGIApplication):
        self._address = (host, port)
        self._app = app
        self._stop = False

        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    @property
    def address(self):
        return self._address

    def signal_handler(self, signum, frame):
        logger.info("Received signal %s", signum)
        self._stop = True

    def get_environ(self, client_socket: socket.socket) -> dict:
        data_lines = client_socket.recv(1024).decode("utf-8").split("\r\n")
        method, path, version = data_lines.pop(0).split(" ")
        environ = {
            "REQUEST_METHOD": method,
            "PATH_INFO": path,
            "SERVER_PROTOCOL": version,
            "SERVER_NAME": self.address[0],
            "SERVER_PORT": str(self.address[1]),
            "wsgi.version": (1, 0),
            "wsgi.url_scheme": "http",

        }
        for line in data_lines:
            if line == "":
                break
            header_name, header_value = line.split(": ", 1)
            environ[header_name] = header_value

        if "Content-Length" in environ:
            environ["wsgi.input"] = io.StringIO("\r\n".join(data_lines))

        return environ

    def handle_connection(self, conn: socket.socket, address: tuple):
        with conn:
            environ = self.get_environ(conn)

            def start_response(status: str, headers: list[tuple[str, str]], exc_info=None, /):
                conn.send(b"HTTP/1.1 " + status.encode() + b"\r\n")
                for name, value in headers:
                    conn.send(name.encode() + b": " + value.encode() + b"\r\n")
                conn.send(b"\r\n")
                return conn.send

            response = self._app(environ, start_response)
            for data in response:
                conn.send(data)
        return conn, address

    def run(self):
        logger.info("Server running on %s", self.address)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind(self.address)
            server_socket.listen()
            server_socket.setblocking(False)
            while not self._stop:
                try:
                    conn, address = server_socket.accept()
                    logger.debug("Accepted connection from %s", address)

                    conn.setblocking(True)
                    self.handle_connection(conn, address)

                except BlockingIOError:
                    continue

            logger.info("Server stopped")
