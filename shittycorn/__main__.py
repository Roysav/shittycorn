import shittycorn
import argparse
import pydoc


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--host", help="host ip address",
        default="0.0.0.0",
    )
    parser.add_argument(
        "-p", "--port", help="port",
        type=int, default=8080,
    )
    parser.add_argument(
        "app",
        help="WSGI compatible application",
    )
    args = parser.parse_args()

    host = args.host
    port = args.port
    app = pydoc.locate(args.app)

    server = shittycorn.Server(host, port, app)
    server.run()


if __name__ == "__main__":
    main()
