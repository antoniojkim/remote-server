mod app;

extern crate rmp_serde as rmps;
extern crate rmpv;
extern crate serde_json;

use std::convert::TryFrom;
use std::env;
use std::fs;
use std::io::Read;
use std::net::{TcpListener, TcpStream};

use app::build_app;
use emacs_remote::handle::Handle;
use emacs_remote::info::ServerInfo;
use emacs_remote::messages::index::IndexRequest;
use emacs_remote::messages::messagetype::MessageType;

fn handle_connection(stream: &mut TcpStream, server_info: &ServerInfo) -> Result<(), ()> {
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
            return request.handle(stream, server_info);
        }
        _ => {
            println!("Invalid type: {:?}", msgtype);
            return Err(());
        }
    }
}

fn main() {
    let matches = build_app().get_matches_from(env::args_os());

    let server_info = ServerInfo {
        server_path: matches.value_of("server_path").unwrap().to_string(),
    };

    let result = fs::create_dir_all(server_info.server_path.clone());
    assert!(result.is_ok());

    let listener =
        TcpListener::bind(format!("localhost:{}", matches.value_of("port").unwrap())).unwrap();

    for stream in listener.incoming() {
        let mut stream = stream.unwrap();

        if !handle_connection(&mut stream, &server_info).is_ok() {
            println!("Failed to handle stream");
        }
    }
}
