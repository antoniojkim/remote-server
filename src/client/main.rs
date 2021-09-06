extern crate rmp_serde as rmps;

use std::{io::Write, net::TcpStream};

use rmps::Serializer;
use serde::ser::Serialize;

use emacs_remote::messages::index::IndexRequest;

fn main() {
    let mut client = TcpStream::connect("localhost:9130").unwrap();

    let request = IndexRequest::new(
        0,                       // prev_hash
        "test path".to_string(), // index_path
    );

    let buffer = rmps::encode::to_vec(&request).unwrap();
    client.write(&buffer).unwrap();
}
