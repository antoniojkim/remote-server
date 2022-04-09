use std::net::UdpSocket;
use std::sync::{Arc, Barrier};
use std::thread;
use std::time::Duration;

fn main() {
    println!("Prototype");

    let server_daemon_address = "localhost:9130";
    let client_daemon_address = "localhost:9131";
    // let client_interface_address = "localhost:9132";

    let barrier = Arc::new(Barrier::new(3));

    let b1 = Arc::clone(&barrier);
    let server_daemon = thread::spawn(move || {
        let socket = UdpSocket::bind(server_daemon_address).expect("couldn't bind to address");
        socket.set_read_timeout(Some(Duration::from_secs(2)));

        b1.wait();

        let mut buf = [0; 10];
        match socket.recv_from(&mut buf) {
            Ok((num_bytes, src_addr)) => {
                println!(
                    "server daemon received {} bytes from {}",
                    num_bytes, src_addr
                );

                let response = [0; 10];
                socket
                    .send_to(&response, src_addr)
                    .expect("couldn't send data");
            }
            Err(e) => println!("server daemon recv function failed: {:?}", e),
        }

        b1.wait();
    });

    let b2 = Arc::clone(&barrier);
    let client_daemon = thread::spawn(move || {
        let socket = UdpSocket::bind(client_daemon_address).expect("couldn't bind to address");
        socket.set_read_timeout(Some(Duration::from_secs(2)));

        b2.wait();

        let mut buf = [0; 10];
        match socket.recv_from(&mut buf) {
            Ok((num_bytes, src_addr)) => {
                println!(
                    "client daemon received {} bytes from {}",
                    num_bytes, src_addr
                );

                socket
                    .send_to(&buf, server_daemon_address)
                    .expect("couldn't send data");

                let response = [0; 10];
                socket
                    .send_to(&response, src_addr)
                    .expect("couldn't send data");
            }
            Err(e) => println!("client daemon recv function failed: {:?}", e),
        }

        b2.wait();
    });

    let b3 = Arc::clone(&barrier);
    let client_interface = thread::spawn(move || {
        let socket = UdpSocket::bind("localhost:0").expect("couldn't bind to address");
        socket.set_read_timeout(Some(Duration::from_secs(1)));

        b3.wait();

        let buf = [0; 10];
        socket
            .send_to(&buf, client_daemon_address)
            .expect("couldn't send data");

        let mut response = [0; 10];
        match socket.recv(&mut response) {
            Ok(received) => println!(
                "client interface received {} bytes {:?}",
                received,
                &response[..received]
            ),
            Err(e) => println!("interface recv function failed: {:?}", e),
        }

        b3.wait();
    });

    client_interface
        .join()
        .expect("Failed to join client interface thread");
    client_daemon
        .join()
        .expect("Failed to join client daemon thread");
    server_daemon
        .join()
        .expect("Failed to join server daemon thread");
}
