use std::fs;
use std::net::{SocketAddr, UdpSocket};

use clap::Parser;

mod utils;
use utils::workspace::Workspace;

struct Daemon {
    socket: UdpSocket,
    workspace: Workspace,
}

impl Daemon {
    fn new(project_dir: &String) -> Daemon {
        let daemon = Daemon {
            socket: UdpSocket::bind("localhost:0").expect("Failed to bind UDP port"),
            workspace: Workspace::new(project_dir),
        };

        daemon.write_port();

        return daemon;
    }

    fn write_port(&self) {
        let daemon_addr_file = self.workspace.daemon_addr_file();

        fs::write(
            daemon_addr_file,
            self.socket.local_addr().unwrap().to_string(),
        )
        .expect("Unable to write addr to file");
    }

    fn listen(&self) {}
}

impl Drop for Daemon {
    fn drop(&mut self) {
        let daemon_addr_file = self.workspace.daemon_addr_file();
        fs::remove_file(daemon_addr_file).expect("Unable to remove daemon port file");
    }
}

#[derive(Parser, Debug)]
#[clap(author, version, about, long_about = None)]
struct Args {
    #[clap(short, long)]
    project_dir: String,

    #[clap(short, long, default_value = "")]
    client_addr: String,
}

fn main() {
    let args = Args::parse();

    let daemon = Daemon::new(&args.project_dir);

    let client_socket_addr: SocketAddr = args
        .client_addr
        .as_str()
        .parse()
        .expect("Invalid client address");

    let addr = daemon.socket.local_addr().unwrap().to_string();
    println!("Sending address to client: {}", addr);

    daemon
        .socket
        .send_to(addr.as_bytes(), &client_socket_addr)
        .expect("Failed to send daemon address to client");

    daemon.listen();
}
