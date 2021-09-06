extern crate rmp_serde as rmps;
extern crate rmpv;
extern crate serde_json;

use std::io::Read;
use std::net::{TcpListener, TcpStream};

use emacs_remote::messages::index::IndexRequest;
use emacs_remote::messages::messagetype::MessageType;

fn handle_connection(mut stream: TcpStream) -> Result<(), Box<std::error::Error>> {
    let mut buf = [0; 1024];
    stream.read(&mut buf).unwrap();

    let value: rmpv::Value = rmps::decode::from_read_ref(&buf)?;
    println!("Request: {}", serde_json::to_string(&value)?);

    assert!(value.is_array());
    let array = value.as_array().unwrap();

    assert!(value[0].is_u64());
    let msgtype = value[0].as_u64().unwrap();

    match msgtype {
        msgtype if msgtype == MessageType::IndexRequest as u64 => {
            let request: IndexRequest = rmp_serde::from_read_ref(&buf).unwrap();
            println!("IndexRequest: {:?}", request);
        }
        _ => println!("Invalid type: {}", msgtype),
    }

    Ok(())
}

fn main() {
    let listener = TcpListener::bind("localhost:9130").unwrap();

    for stream in listener.incoming() {
        let stream = stream.unwrap();

        handle_connection(stream);
    }
}
