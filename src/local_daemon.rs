use std::io::{Read, Write};
use std::net::{SocketAddr, TcpListener, TcpStream, UdpSocket};
use std::process::Command;
use std::sync::{Arc, Mutex, RwLock};
use std::time::Duration;
use std::{fs, thread};

use clap::Parser;

mod requests;
use requests::payload::Payload;

mod utils;
use utils::event::Event;
use utils::workspace::Workspace;

struct Daemon {
    // UDP socket for listening to request from remote daemon
    socket: Arc<UdpSocket>,
    remote_socket: Option<UdpSocket>,
    // TCP listener for listening to request from local clients
    stream: Arc<TcpListener>,
    workspace: Workspace,
}

impl Daemon {
    fn new(project_dir: &String) -> Daemon {
        let daemon = Daemon {
            socket: Arc::new(UdpSocket::bind("localhost:0").expect("Failed to bind UDP port")),
            remote_socket: None,
            stream: Arc::new(TcpListener::bind("localhost:0").expect("Failed to bind TCP port")),
            workspace: Workspace::new(project_dir),
        };

        daemon.write_port();

        return daemon;
    }

    fn get_socket_addr(&self) -> String {
        self.socket.local_addr().unwrap().to_string()
    }

    fn write_port(&self) {
        let daemon_addr_file = self.workspace.daemon_addr_file();

        fs::write(
            daemon_addr_file,
            self.stream.local_addr().unwrap().to_string(),
        )
        .expect("Unable to write addr to file");
    }

    fn start_remote_daemon(&self) {
        // TODO: Implement this connection via ssh
        let output = Command::new("emacs-remote-client")
            .args([
                "--project-dir",
                self.workspace.project_dir().to_str().unwrap(),
            ])
            .args(["--client-addr", self.get_socket_addr().as_str()])
            .output()
            .expect("Failed to start emacs-remote-client. Make sure it is installed and discoverable in the PATH");

        let output = std::str::from_utf8(output.stdout.as_slice())
            .expect("Unable to read remote client output");
        println!("emacs-remote-client output: {}", output);
    }

    fn stop_remote_daemon(&self) {}

    fn handle_stream_request(stream: &mut TcpStream, addr: &mut SocketAddr) -> bool {
        println!("{}", addr);

        let mut payload = [0; 1024];
        stream
            .read(&mut payload)
            .expect("Could not read request from emacs-local-client");

        let payload = Payload::from_bytes(&payload.to_vec()).expect("Could not parse payload");
        let request = payload.to_request();
        let response = request.run();

        if response.is_some() {
            stream
                .write(&response.unwrap().as_bytes())
                .expect("Could not send request to emacs-local-daemon");
        }
        return true;
    }

    fn listen(&self) {
        // TODO: Change to `false` once socket logic is implemented
        let mut finished = Event::new();
        finished.clear();

        let socket_finished = finished.clone();
        let socket = self.socket.clone();
        // Listen for requests from remote daemon
        let socket_thread = thread::spawn(move || {
            while !socket_finished.is_set() {
                let mut buf = [0; 10];
                let (amt, src) = socket.recv_from(&mut buf).unwrap();

                // TODO: Remove once socket logic is implemented
                break;
            }
        });

        // Listen for requests from local clients
        while !finished.is_set() {
            match self.stream.accept() {
                Ok((mut stream, mut addr)) => {
                    let mut stream_finished = finished.clone();
                    thread::spawn(move || {
                        let set_finished = Daemon::handle_stream_request(&mut stream, &mut addr);

                        if set_finished {
                            stream_finished.set()
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

        self.stop_remote_daemon();
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

    // Broadcast address to client
    if !args.client_addr.is_empty() {
        let client_socket_addr: SocketAddr = args
            .client_addr
            .as_str()
            .parse()
            .expect("Invalid client address");

        let addr = daemon.stream.local_addr().unwrap().to_string();
        println!("Sending address to client: {}", addr);

        daemon
            .socket
            .send_to(addr.as_bytes(), &client_socket_addr)
            .expect("Failed to send daemon address to client");
    }

    daemon.start_remote_daemon();

    daemon.listen();
}
