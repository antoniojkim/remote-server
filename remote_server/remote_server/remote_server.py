import zmq


@dataclass
class RemoteServer:
    workspace: Workspace

    def listen(self):
        context = zmq.Context()
        socket = context.socket(zmq.REP)

        self.port = socket.bind_to_random_port('tcp://*', min_port=6000, max_port=6100, max_tries=100)
        self.port_file = self.workspace.workspace_path.joinpath("port.txt")
        self.port_file.write_text(str(self.port))

        # Remove port file at exit
        atexit.register(lambda: self.port_file.unlink())

        # from zmq import ssh
        # ssh.tunnel_connection(sock, "tcp://127.0.0.1:5555", "10.0.1.2")




def main(args):
    server = RemoteServer(workspace=Workspace(host="", workspace=args.workspace))
    server.listen()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.parse_args("--host", type=str, help="IP address or name of the host")
    parser.parse_args(
        "--workspace",
        type=str,
        help="Path to the project workspace on the remote server",
    )
    main(parser.parse_args())
