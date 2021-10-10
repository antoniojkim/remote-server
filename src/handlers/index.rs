extern crate dirs;
extern crate flate2;
extern crate rmp_serde as rmps;

use std::fs;
use std::io::Write;
use std::net::TcpStream;
use std::path::PathBuf;

use flate2::write::GzEncoder;
use flate2::Compression;

use crate::handle::{HandleClientDaemon, HandleServerDaemon};
use crate::messages::index::{IndexRequest, IndexResponse};
use crate::structs::client::ClientDaemon;
use crate::structs::server::ServerDaemon;
use crate::utils;
use crate::utils::{hash, shutil};

impl HandleClientDaemon for IndexRequest {
    fn handle(&self, stream: &mut TcpStream, client_daemon: &mut ClientDaemon) -> Result<(), ()> {
        // if client_daemon.server_send(&self).is_err() {
        //     return Err(());
        // }

        // let mut response = client_daemon.server_recv::<IndexResponse>().unwrap();
        // // response.save(client_daemon.client_path);

        // client_daemon.update_index_hash(response.hash);

        // let mut local_index_path = PathBuf::new();
        // local_index_path.push(client_daemon.client_path.clone());
        // local_index_path.push(format!("{}.index", response.hash));

        // if utils::stream::send(stream, &mut response).is_err() {
        //     return Err(());
        // }

        Ok(())
    }
}

impl HandleServerDaemon for IndexRequest {
    fn handle(&self, stream: &mut TcpStream, server_daemon: &mut ServerDaemon) -> Result<(), ()> {
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
