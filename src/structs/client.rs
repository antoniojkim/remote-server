extern crate rmp_serde as rmps;
extern crate ssh;

use std::convert::TryFrom;
use std::fs;
use std::io::Read;
use std::net::{TcpListener, TcpStream};
use std::path::PathBuf;
use std::time::Instant;

use serde::de::DeserializeOwned;
use serde::{Deserialize, Serialize};

use crate::handle::HandleClientDaemon;
use crate::messages::index::IndexRequest;
use crate::messages::messagetype::{MessageType, MessageTypeTrait};
use crate::utils;

#[derive(Deserialize, Serialize, Debug)]
pub struct ClientDaemon {
    host: String,
    workspace: String,
    // connection info
    pub client_path: String,
    client_port: String,
    server_port: String,

    // streams
    #[serde(skip)]
    server: Option<TcpStream>,

    // ssh connection
    #[serde(skip)]
    ssh_session: Option<ssh::Session>,

    // state
    current_index_hash: u64,
}

impl ClientDaemon {
    pub fn new(
        host: String,
        workspace: String,
        client_path: String,
        client_port: String,
        server_port: String,
    ) -> Result<ClientDaemon, ()> {
        let mut workspace_path = PathBuf::new();
        workspace_path.push(client_path.clone());
        fs::create_dir_all(workspace_path.clone()).expect("Unable to create client path");

        workspace_path.push("workspaces");
        fs::create_dir_all(workspace_path.clone()).expect("Unable to create workspace path");

        workspace_path.push(format!(
            "{}-{}.workspace",
            host,
            utils::hash::hash(&workspace_path),
        ));

        if workspace_path.as_path().exists() {
            let data = fs::read(workspace_path.as_path()).unwrap();
            let mut client: ClientDaemon = rmps::from_read_ref(&data).unwrap();

            if client.host != host
                || client.workspace != workspace
                || client.client_path != client_path
            {
                return Err(());
            }
            client.client_port = client_port;
            client.server_port = server_port;
            return Ok(client);
        }

        Ok(ClientDaemon {
            host,
            workspace,
            client_path,
            client_port: client_port.clone(),
            server_port: server_port.clone(),
            server: None,
            ssh_session: None,
            // initialize state
            current_index_hash: 0,
        })
    }

    pub fn init(&mut self) {
        self.reset_tcp_connection()
            .expect("Unable to establish tcp connection");
        self.reset_ssh_session()
            .expect("Unable to establish ssh connection");
    }

    pub fn reset_tcp_connection(&mut self) -> Result<(), ()> {
        let now = Instant::now();

        // Establishing TCP connection with server
        let result = TcpStream::connect(format!("localhost:{}", self.server_port));
        if result.is_err() {
            return Err(());
        }
        self.server = Some(result.unwrap());

        println!(
            "tcp connection established in {} milliseconds",
            now.elapsed().as_millis()
        );

        Ok(())
    }

    pub fn reset_ssh_session(&mut self) -> Result<(), ()> {
        let now = Instant::now();

        // Establishing ssh connection with server
        let mut session = ssh::Session::new().unwrap();
        session.set_host(&self.host).unwrap();
        session.parse_config(None).unwrap();
        session.connect().unwrap();

        if session.is_server_known().is_err() {
            return Err(());
        }
        session.userauth_publickey_auto(None).unwrap();

        self.ssh_session = Some(session);

        println!(
            "ssh connection established in {} milliseconds",
            now.elapsed().as_millis()
        );

        Ok(())
    }

    pub fn server_send<T: Serialize>(&mut self, message: &T) -> Result<(), ()> {
        if !self.server.is_some() {
            self.reset_tcp_connection()
                .expect("Unable to establish tcp connection");
        }
        return utils::stream::send(self.server.as_mut().unwrap(), message);
    }

    pub fn server_recv<T>(&mut self) -> Result<T, ()>
    where
        T: DeserializeOwned + MessageTypeTrait,
    {
        if !self.server.is_some() {
            self.reset_tcp_connection()
                .expect("Unable to establish tcp connection");
        }
        return utils::stream::recv::<T>(self.server.as_mut().unwrap());
    }

    pub fn update_index_hash(&mut self, hash: u64) {
        self.current_index_hash = hash;
    }

    pub fn listen(&mut self) {
        let receiver = TcpListener::bind(format!("localhost:{}", self.client_port)).unwrap();

        for stream in receiver.incoming() {
            let mut stream = stream.unwrap();

            if self.handle(&mut stream).is_err() {
                println!("Failed to handle stream");
            }
        }
    }

    fn handle(&mut self, stream: &mut TcpStream) -> Result<(), ()> {
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
                return request.handle(stream, self);
            }
            _ => {
                println!("Invalid type: {:?}", msgtype);
                return Err(());
            }
        }
    }
}

// fn test_connection() {
//     let mut client = TcpStream::connect("localhost:9130").unwrap();

//     let request = IndexRequest::new(
//         0,                                                               // prev_hash
//         "/Users/antoniokim/Documents/Projects/emacs-remote".to_string(), // index_path
//     );

//     let now = Instant::now();

//     let buffer = rmps::encode::to_vec(&request).unwrap();
//     client.write(&buffer).unwrap();

//     if handle_response(&mut &client).is_err() {
//         panic!("Unable to handle response");
//     }

//     println!(
//         "Request handled in {} milliseconds",
//         now.elapsed().as_millis()
//     );
// }

// fn test_ssh() {
//     let now = Instant::now();

//     let mut session = ssh::Session::new().unwrap();
//     session.set_host("cerebras").unwrap();
//     session.parse_config(None).unwrap();
//     session.connect().unwrap();
//     println!("{:?}", session.is_server_known());
//     session.userauth_publickey_auto(None).unwrap();

//     println!(
//         "ssh connection established in {} milliseconds",
//         now.elapsed().as_millis()
//     );

//     for _i in 0..10 {
//         thread::sleep(Duration::from_millis(10000));

//         let now = Instant::now();

//         let mut scp = session
//             .scp_new(
//                 ssh::READ,
//                 "/net/antonio-dev/srv/nfs/antonio-data/ws/.emacs_remote/server/index_17645410072557185842.mp",
//             )
//             .unwrap();
//         scp.init().unwrap();
//         loop {
//             match scp.pull_request().unwrap() {
//                 ssh::Request::NEWFILE => {
//                     let mut buf: Vec<u8> = vec![];
//                     scp.accept_request().unwrap();
//                     scp.reader().read_to_end(&mut buf).unwrap();

//                     println!(
//                         "Took {} milliseconds to read file",
//                         now.elapsed().as_millis()
//                     );
//                     break;
//                 }
//                 ssh::Request::WARNING => {
//                     scp.deny_request().unwrap();
//                     break;
//                 }
//                 _ => scp.deny_request().unwrap(),
//             }
//         }
//     }
// }
