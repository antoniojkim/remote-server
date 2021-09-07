extern crate rmp_serde as rmps;
extern crate rmpv;
extern crate serde_json;

use std::convert::TryFrom;
use std::io::Read;
use std::net::{TcpListener, TcpStream};

use emacs_remote::handle::Handle;
use emacs_remote::messages::index::IndexRequest;
use emacs_remote::messages::messagetype::MessageType;

fn handle_connection(mut stream: TcpStream) -> Result<(), ()> {
    let mut buf = [0; 1024];
    stream.read(&mut buf).unwrap();

    let value: rmpv::Value = rmps::decode::from_read_ref(&buf).unwrap();
    println!("Request: {}", serde_json::to_string(&value).unwrap());

    assert!(value.is_array());
    assert!(value[0].is_u64());
    let msgtype = MessageType::try_from(value[0].as_u64().unwrap()).unwrap();

    match msgtype {
        MessageType::IndexRequest => {
            let request: IndexRequest = rmp_serde::from_read_ref(&buf).unwrap();
            request.handle();
            return Ok(());
        }
        _ => {
            println!("Invalid type: {:?}", msgtype);
            return Err(());
        }
    }
}

fn main() {
    let listener = TcpListener::bind("localhost:9130").unwrap();

    for stream in listener.incoming() {
        let stream = stream.unwrap();

        if !handle_connection(stream).is_ok() {
            println!("Failed to handle stream");
        }
    }
}
