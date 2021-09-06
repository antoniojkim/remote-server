extern crate rmp_serde as rmps;

use std::{io::Write, net::TcpStream};

use rmps::Serializer;
use serde::ser::Serialize;

use emacs_remote::messages::index::IndexMessageRequest;

fn main() {
    let mut client = TcpStream::connect("localhost:9130").unwrap();

    let request = IndexMessageRequest {
        prev_hash: 0,
        index_path: "TEsting".to_string(),
    };

    let mut buf = Vec::new();
    request.serialize(&mut Serializer::new(&mut buf)).unwrap();

    client.write(&buf).unwrap();
}
