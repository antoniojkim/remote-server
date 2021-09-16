extern crate rmp_serde as rmps;
extern crate ssh;

use std::convert::TryFrom;
use std::io::{Read, Write};
use std::net::TcpStream;
use std::thread;
use std::time::{Duration, Instant};

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

fn test_connection() {
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

fn test_ssh() {
    let now = Instant::now();

    let mut session = ssh::Session::new().unwrap();
    session.set_host("AML").unwrap();
    session.parse_config(None).unwrap();
    session.connect().unwrap();
    println!("{:?}", session.is_server_known());
    session.userauth_publickey_auto(None).unwrap();

    println!(
        "ssh connection established in {} milliseconds",
        now.elapsed().as_millis()
    );

    for i in 0..10 {
        thread::sleep(Duration::from_millis(10000));

        let now = Instant::now();

        let mut scp = session
            .scp_new(
                ssh::READ,
                "/home/antonio/.emacs_remote/server/index_monolith.txt.gz",
            )
            .unwrap();
        scp.init().unwrap();
        loop {
            match scp.pull_request().unwrap() {
                ssh::Request::NEWFILE => {
                    let mut buf: Vec<u8> = vec![];
                    scp.accept_request().unwrap();
                    scp.reader().read_to_end(&mut buf).unwrap();

                    println!(
                        "Took {} milliseconds to read file",
                        now.elapsed().as_millis()
                    );
                    break;
                }
                ssh::Request::WARNING => {
                    scp.deny_request().unwrap();
                    break;
                }
                _ => scp.deny_request().unwrap(),
            }
        }
    }
}

fn main() {}
