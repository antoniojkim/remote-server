use std::net::UdpSocket;

mod utils;

use utils::workspace::Workspace;

struct Client {
    socket: UdpSocket,
    workspace: Workspace,
}

impl Client {
    fn init(workspace: &String) -> Client {
        let client = Client {
            socket: UdpSocket::bind("localhost:0").expect("Failed to bind UDP port"),
            workspace: Workspace::init(workspace),
        };
        return client;
    }
}

fn main() {
    println!("Emacs Local Client");

    let workspace = "/Users/antoniokim/Documents/Projects/emacs-remote".to_string();
    let client = Client::init(&workspace);

    println!(
        "{} -> {}",
        client.workspace,
        client.socket.local_addr().unwrap()
    );
}
