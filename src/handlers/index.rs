extern crate dirs;
extern crate flate2;
extern crate rmp_serde as rmps;

use std::fs;
use std::io::Write;
use std::net::TcpStream;
use std::path::PathBuf;

use flate2::write::GzEncoder;
use flate2::Compression;

use super::super::handle::HandleServer;
use super::super::messages::index::{IndexRequest, IndexResponse};
use super::super::structs::ServerDaemon;
use super::super::utils::{hash, shutil};

impl HandleServer for IndexRequest {
    fn handle(&self, stream: &mut TcpStream, server_daemon: &ServerDaemon) -> Result<(), ()> {
        println!("IndexRequest: {:?}", self);

        let mut files = shutil::find("", &self.index_path).unwrap();
        files.sort();

        let h = hash::hash(&files);

        let mut index_path = PathBuf::new();
        index_path.push(server_daemon.server_path.clone());
        index_path.push(format!("{}.index", h));

        let mut e = GzEncoder::new(Vec::new(), Compression::default());
        for file in &files {
            e.write_all(file.as_bytes())
                .expect(format!("Failed to write file: {}", file).as_str());
            e.write_all(b";")
                .expect(format!("Failed to write file: {}", file).as_str());
        }
        let buffer = e.finish().unwrap();

        if fs::write(index_path.as_path(), buffer).is_err() {
            return Err(());
        }

        let response = IndexResponse::new(
            h,                                        // hash
            index_path.to_str().unwrap().to_string(), // path_to_index_file
        );

        let buffer = rmps::encode::to_vec(&response).unwrap();
        stream.write(&buffer).unwrap();
        stream.flush().unwrap();

        Ok(())
    }
}
