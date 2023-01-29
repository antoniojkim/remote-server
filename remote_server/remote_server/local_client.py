import argparse
from dataclasses import dataclass
from workspace import Workspace


@dataclass
class LocalClient:
    workspace: Workspace


def main(args):
    client = LocalClient(workspace=Workspace())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.parse_args("--host", type=str, help="IP address or name of the host")
    parser.parse_args("--remote_server_path", type=str, help="Path to the remote server's workspace")
    main(parser.parse_args())
