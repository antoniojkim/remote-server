use std::io::{Read, Write};
use std::net::{SocketAddr, TcpStream, UdpSocket};
use std::process::Command;
use std::time::Duration;

use clap::{Parser, Subcommand};

mod requests;
use requests::exit_request::ExitRequest;
use requests::msg_request::MsgRequest;
use requests::payload::Payload;
use requests::request::Request;

mod utils;
use serde::Serialize;
use utils::workspace::Workspace;

use crate::requests::shell_request::ShellRequest;

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

    fn send_to_daemon(&self, socket: &SocketAddr, payload: &Payload) -> Result<u16, u16> {
        let mut stream =
            TcpStream::connect(socket).expect("Failed to connect to emacs-local-daemon");

        stream
            .write(&payload.as_bytes())
            .expect("Could not send request to emacs-local-daemon");

        let mut payload = [0; 1024];
        stream
            .read(&mut payload)
            .expect("Did not receive response from emacs-local-daemon");

        let payload = Payload::from_bytes(&payload.to_vec()).expect("Failed to parse payload");
        let response = payload.to_response();
        response.run()
    }
}

#[derive(Parser)]
#[clap(author, version, about, long_about = None)]
struct Args {
    #[clap(short, long)]
    project_dir: String,

    #[clap(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Run a shell command
    Shell { args: Vec<String> },
    /// Exit the daemon
    Exit {},
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

    let payload = match args.command {
        Commands::Shell { args } => {
            Payload::from_request(&ShellRequest::new(client.workspace.project_dir(), args))
        }
        Commands::Exit {} => Payload::from_request(&ExitRequest::new()),
    };

    client
        .send_to_daemon(&socket.unwrap(), &payload)
        .expect("Failed to run response");
}
