use std::net::{SocketAddr, TcpListener, TcpStream, UdpSocket};
use std::sync::{Arc, Mutex, RwLock};
use std::time::Duration;
use std::{fs, thread};

use clap::Parser;

mod utils;
use utils::workspace::Workspace;

struct Daemon {
    // UDP socket for listening to request from remote daemon
    socket: Arc<UdpSocket>,
    // TCP listener for listening to request from local clients
    stream: Arc<TcpListener>,
    workspace: Workspace,
}

impl Daemon {
    fn new(project_dir: &String) -> Daemon {
        let daemon = Daemon {
            socket: Arc::new(UdpSocket::bind("localhost:0").expect("Failed to bind UDP port")),
            stream: Arc::new(TcpListener::bind("localhost:0").expect("Failed to bind TCP port")),
            workspace: Workspace::new(project_dir),
        };

        daemon.write_port();

        return daemon;
    }

    fn write_port(&self) {
        let daemon_addr_file = self.workspace.daemon_addr_file();

        fs::write(
            daemon_addr_file,
            self.stream.local_addr().unwrap().to_string(),
        )
        .expect("Unable to write addr to file");
    }

    fn handle_stream_request(stream: &mut TcpStream, addr: &mut SocketAddr) -> bool {
        return true;
    }

    fn listen(&self) {
        // TODO: Change to `false` once socket logic is implemented
        let finished = Arc::new(Mutex::new(true));

        let socket_finished = finished.clone();
        let socket = self.socket.clone();
        // Listen for requests from remote daemon
        let socket_thread = thread::spawn(move || {
            loop {
                // Check exit condition
                {
                    let is_finished = socket_finished.lock().unwrap();
                    if *is_finished {
                        return;
                    }
                }
                let mut buf = [0; 10];
                let (amt, src) = socket.recv_from(&mut buf).unwrap();

                // TODO: Remove once socket logic is implemented
                break;
            }
        });

        // Listen for requests from clients
        loop {
            // Check exit condition
            {
                let is_finished = finished.lock().unwrap();
                if *is_finished {
                    break;
                }
            }
            match self.stream.accept() {
                Ok((mut stream, mut addr)) => {
                    let socket_finished = finished.clone();
                    thread::spawn(move || {
                        let set_finished = Daemon::handle_stream_request(&mut stream, &mut addr);

                        if set_finished {
                            let mut is_finished = socket_finished.lock().unwrap();
                            *is_finished = true;
                        }
                    });

                    println!("new client: {:?}", addr)
                }
                Err(e) => println!("couldn't get client: {:?}", e),
            }
        }

        socket_thread.join().expect("Unable to join socket thread");
        // thread::sleep(Duration::from_secs(5));
    }
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
