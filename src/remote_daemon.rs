use std::io::Write;
use std::net::{SocketAddr, TcpListener, TcpStream, UdpSocket};
use std::sync::{Arc, Mutex, RwLock};

use clap::Parser;

mod utils;
use utils::workspace::Workspace;

struct Daemon {
    // UDP socket for listening to request from remote daemon
    socket: Arc<UdpSocket>,
    client_addr: String, // SocketAddr,
    encryption_key: i64,
    workspace: Workspace,
}

impl Daemon {
    fn new(project_dir: &String, client_addr: &String) -> Daemon {
        let daemon = Daemon {
            socket: Arc::new(UdpSocket::bind("localhost:0").expect("Failed to bind UDP port")),
            client_addr: client_addr.clone(), //.as_str().parse().expect("Invalid client address"),
            encryption_key: 123456,
            workspace: Workspace::new(project_dir),
        };

        return daemon;
    }

    fn notify_client(&self, listener_addr: &String) {
        let mut stream =
            TcpStream::connect(listener_addr).expect("ERROR: could not connect to remote client");

        let msg = format!(
            "{};{:#x}",
            self.socket.local_addr().unwrap().to_string(),
            self.encryption_key
        );
        stream
            .write(msg.as_bytes())
            .expect("ERROR: could not send message to remote client");
    }
}

#[derive(Parser, Debug)]
#[clap(author, version, about, long_about = None)]
struct Args {
    #[clap(short, long)]
    project_dir: String,

    #[clap(short, long)]
    client_addr: String,

    #[clap(short, long)]
    listener_addr: String,
}

fn main() {
    let args = Args::parse();

    let daemon = Daemon::new(&args.project_dir, &args.client_addr);

    daemon.notify_client(&args.listener_addr);
}
