use std::{
    fs,
    net::{TcpListener, TcpStream},
    path::PathBuf,
};

pub struct ServerDaemon {
    pub emacs_remote_path: String,
    pub port: String,
    pub workspace: String,
}

impl ServerDaemon {
    pub fn new(emacs_remote_path: String, port: String, workspace: String) -> ServerDaemon {
        let mut workspace_path = PathBuf::new();
        workspace_path.push(emacs_remote_path.clone());
        workspace_path.push("server");
        fs::create_dir_all(workspace_path.clone()).expect("Unable to create server path");

        workspace_path.push("workspaces");
        fs::create_dir_all(workspace_path.clone()).expect("Unable to create workspace path");

        ServerDaemon {
            emacs_remote_path,
            port,
            workspace,
        }
    }

    pub fn init(&mut self) {}

    pub fn listen(&mut self) {
        let listener = TcpListener::bind(format!("localhost:{}", self.port)).unwrap();

        for stream in listener.incoming() {
            let mut stream = stream.unwrap();

            if self.handle(&mut stream).is_err() {
                println!("Failed to handle stream");
            }
        }
    }

    fn handle(&mut self, stream: &mut TcpStream) -> Result<(), ()> {
        println!("Received Tcp request");
        Ok(())
    }
}
