use std::fs;
use std::net::{SocketAddr, UdpSocket};
use std::process::Command;
use std::thread;
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

    fn check_daemon(&self) -> Option<SocketAddr> {
        let mut daemon_port_file = self.workspace.path().clone();
        daemon_port_file.push("daemon.port");

        // If daemon already exists, return the address
        if daemon_port_file.exists() {
            let daemon_port =
                fs::read_to_string(daemon_port_file).expect("Unable to read daemon file");
            return Some(SocketAddr::from((
                [127, 0, 0, 1],
                daemon_port.parse::<u16>().unwrap(),
            )));
        }

        self.start_daemon();

        None
    }

    fn start_daemon(&self) {
        Command::new("emacs-local-daemon")
            .spawn()
            .expect("Failed to start emacs-local-daemon");
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
