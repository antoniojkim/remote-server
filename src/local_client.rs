use std::net::{SocketAddr, UdpSocket};
use std::process::Command;
use std::time::Duration;

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
}

fn main() {
    println!("Emacs Local Client");

    let project_dir = "/Users/antoniokim/Documents/Projects/emacs-remote".to_string();
    let client = Client::new(&project_dir);

    // Check if daemon exists, otherwise start a new one
    client.check_daemon();

    println!(
        "{} -> {}",
        client.workspace,
        client.socket.local_addr().unwrap()
    );
}
