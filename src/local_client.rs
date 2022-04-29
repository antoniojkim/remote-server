use std::io::{Read, Write};
use std::net::{SocketAddr, TcpStream, UdpSocket};
use std::process::Command;
use std::time::Duration;

use clap::Parser;

mod requests;
use requests::init_request::{InitRequest, InitResponse};
use requests::request::{Request, Response};

mod utils;
use utils::workspace::Workspace;

struct Client {
    socket: UdpSocket,
    workspace: Workspace,
}

impl Client {
    fn new(project_dir: &String) -> Client {
        Client {
            socket: UdpSocket::bind("localhost:0").expect("Failed to bind UDP port"),
            workspace: Workspace::new(project_dir),
        }
    }

    fn get_socket_addr(&self) -> String {
        self.socket.local_addr().unwrap().to_string()
    }

    fn check_daemon(&self) -> Option<SocketAddr> {
        let daemon_addr = self.workspace.daemon_addr();

        // If daemon already exists, return the address
        if daemon_addr.is_some() {
            return daemon_addr;
        }

        self.start_daemon();

        self.socket
            .set_read_timeout(Some(Duration::from_secs(3)))
            .expect("Unable to set socket read timeout");

        let mut buf = [0; 16];
        match self.socket.recv_from(&mut buf) {
            Ok((num_bytes, _src_addr)) => {
                let daemon_addr = String::from_utf8((&mut buf[..num_bytes]).to_vec())
                    .expect("Failed to receive daemon address");

                println!("Client received daemon address: {}", daemon_addr);
                return Some(
                    daemon_addr
                        .as_str()
                        .parse()
                        .expect("Invalid daemon address"),
                );
            }
            Err(_) => {
                return self.workspace.daemon_addr();
            }
        }
    }

    fn start_daemon(&self) {
        Command::new("emacs-local-daemon")
            .args([
                "--project-dir",
                self.workspace.project_dir().to_str().unwrap(),
            ])
            .args(["--client-addr", self.get_socket_addr().as_str()])
            .spawn()
            .expect("Failed to start emacs-local-daemon. Make sure it is installed and discoverable in the PATH");
    }

    fn send_to_daemon(&self, socket: &SocketAddr, request: &impl Request) {
        let mut stream =
            TcpStream::connect(socket).expect("Failed to connect to emacs-local-daemon");

        stream
            .write(&request.as_bytes())
            .expect("Could not send request to emacs-local-daemon");

        let mut response = [0; 1024];
        stream
            .read(&mut response)
            .expect("Did not receive response from emacs-local-daemon");

        let response = request.get_response_from_bytes(&response.to_vec());
        response.run().unwrap();
    }
}

#[derive(Parser, Debug)]
#[clap(author, version, about, long_about = None)]
struct Args {
    #[clap(short, long)]
    project_dir: String,
}

fn main() {
    println!("Emacs Local Client");
    let args = Args::parse();

    let client = Client::new(&args.project_dir);

    // Check if daemon exists, otherwise start a new one
    let socket = client.check_daemon();

    if socket.is_none() {
        println!("Unable to connect to emacs-local-daemon");
        return;
    }

    let payload = InitRequest::new();
    client.send_to_daemon(&socket.unwrap(), &payload);
}
