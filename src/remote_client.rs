use std::io::Read;
use std::net::{SocketAddr, TcpListener, UdpSocket};
use std::process::Command;
use std::time::Duration;

use clap::Parser;

mod utils;
use utils::workspace::Workspace;

struct Client {
    project_dir: String,
    client_addr: String,
}

impl Client {
    fn new(project_dir: &String, client_addr: &String) -> Client {
        Client {
            project_dir: project_dir.to_string(),
            client_addr: client_addr.to_string(),
        }
    }

    fn start_daemon(&self) {
        let listener = TcpListener::bind("localhost:0").expect("Failed to bind TCP port");

        Command::new("emacs-remote-daemon")
            .args(["--project-dir", self.project_dir.as_str()])
            .args(["--client-addr", self.client_addr.as_str()])
            .args(["--listener-addr", listener.local_addr().unwrap().to_string().as_str()])
            .spawn()
            .expect("Failed to start emacs-remote-daemon. Make sure it is installed and discoverable in the PATH");

        // Listen for the encryption key and daemon address
        match listener.accept() {
            Ok((mut stream, _addr)) => {
                let mut buf = [0; 256];
                stream
                    .read(&mut buf)
                    .expect("ERROR: Could not receive key from daemon");
                let msg =
                    std::str::from_utf8(&buf).expect("ERROR: Could not read bytes from message");
                println!("{}", msg);
            }
            Err(e) => println!("ERROR: did not receive connection from daemon. {}", e),
        }
    }
}

#[derive(Parser, Debug)]
#[clap(author, version, about, long_about = None)]
struct Args {
    #[clap(short, long)]
    project_dir: String,

    #[clap(short, long)]
    client_addr: String,
}

fn main() {
    let args = Args::parse();

    let client = Client::new(&args.project_dir, &args.client_addr);

    client.start_daemon();
}
