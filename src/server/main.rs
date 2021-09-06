use std::io::Read;
use std::net::{TcpListener, TcpStream};

use rmpv::decode::read_value;

fn handle_connection(mut stream: TcpStream) {
    let mut buffer = [0; 1024];
    stream.read(&mut buffer).unwrap();

    let value = read_value(&mut &buffer[..]).unwrap();

    println!("Request: {:?}", value);
}

fn main() {
    let listener = TcpListener::bind("localhost:9130").unwrap();

    for stream in listener.incoming() {
        let stream = stream.unwrap();

        handle_connection(stream);
    }
}
