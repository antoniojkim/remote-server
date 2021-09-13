extern crate rmp_serde as rmps;

use std::convert::TryFrom;
use std::io::{Read, Write};
use std::net::TcpStream;
use std::time::Instant;

use emacs_remote::messages::index::IndexRequest;
use emacs_remote::messages::messagetype::MessageType;

fn handle_response(stream: &mut &TcpStream) -> Result<(), ()> {
    let mut buf = [0; 1024];
    stream.read(&mut buf).unwrap();

    let value: rmpv::Value = rmps::decode::from_read_ref(&buf).unwrap();
    println!("Response: {}", serde_json::to_string(&value).unwrap());

    assert!(value.is_array());
    assert!(value[0].is_u64());
    let msgtype = MessageType::try_from(value[0].as_u64().unwrap()).unwrap();

    match msgtype {
        MessageType::IndexResponse => {
            // let request: IndexRequest = rmp_serde::from_read_ref(&buf).unwrap();
            // return request.handle(stream, server_info);
            println!("IndexResponse received");
            return Ok(());
        }
        _ => {
            println!("Invalid type: {:?}", msgtype);
            return Err(());
        }
    }
}

fn main() {
    let mut client = TcpStream::connect("localhost:9130").unwrap();

    let request = IndexRequest::new(
        0,                                                               // prev_hash
        "/Users/antoniokim/Documents/Projects/emacs-remote".to_string(), // index_path
    );

    let now = Instant::now();

    let buffer = rmps::encode::to_vec(&request).unwrap();
    client.write(&buffer).unwrap();

    if handle_response(&mut &client).is_err() {
        panic!("Unable to handle response");
    }

    println!(
        "Request handled in {} milliseconds",
        now.elapsed().as_millis()
    );
}
