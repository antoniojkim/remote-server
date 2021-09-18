extern crate dirs;
extern crate rmp_serde as rmps;
extern crate rmpv;
extern crate serde_json;

use std::convert::TryFrom;
use std::env;
use std::fs;
use std::io::Read;
use std::net::{TcpListener, TcpStream};
use std::path::PathBuf;

use clap::{App, Arg};

use emacs_remote::handle::HandleServer;
use emacs_remote::messages::index::IndexRequest;
use emacs_remote::messages::messagetype::MessageType;
use emacs_remote::structs::ServerDaemon;
use emacs_remote::version::VERSION;

fn handle_connection(stream: &mut TcpStream, server_info: &ServerDaemon) -> Result<(), ()> {
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
    // Set up default server path
    let mut default_server_path = PathBuf::new();
    default_server_path.push(dirs::home_dir().unwrap());
    default_server_path.push(".emacs_remote");
    default_server_path.push("server");

    let app = App::new("emacs-remote-server-daemon")
        .version(VERSION)
        .author("antoniojkim <contact@antoniojkim.com>")
        .about("Starts emacs remote server daemon")
        .arg(
            Arg::with_name("workspace")
                .short("w")
                .long("workspace")
                .help("Specifies the workspace to monitor"),
        )
        .arg(
            Arg::with_name("port")
                .short("p")
                .long("port")
                .default_value("9130")
                .help("Specifies the port to listen on"),
        )
        .arg(
            Arg::with_name("server_path")
                .short("s")
                .long("server_path")
                .default_value(default_server_path.to_str().unwrap())
                .help("Path to server directory"),
        );

    let matches = app.get_matches_from(env::args_os());

    let server_daemon = ServerDaemon {
        server_path: matches.value_of("server_path").unwrap().to_string(),
    };

    let result = fs::create_dir_all(server_daemon.server_path.clone());
    assert!(result.is_ok());

    let listener =
        TcpListener::bind(format!("localhost:{}", matches.value_of("port").unwrap())).unwrap();

    for stream in listener.incoming() {
        let mut stream = stream.unwrap();

        if !handle_connection(&mut stream, &server_daemon).is_ok() {
            println!("Failed to handle stream");
        }
    }
}
