use std::clone::Clone;
use std::{net::TcpStream, path::PathBuf};

pub use serde::{Deserialize, Serialize};

use super::messagetype::{MessageType, MessageTypeTrait};

#[derive(Deserialize, Serialize, Clone, Debug)]
pub struct IndexRequest {
    message_type: u64,
    pub prev_hash: u64,
    pub index_path: String,
}

impl MessageTypeTrait for IndexRequest {
    fn messagetype() -> MessageType {
        return MessageType::IndexRequest;
    }
    fn is_valid(&self) -> bool {
        return self.message_type == (Self::messagetype() as u64);
    }
}
impl IndexRequest {
    pub fn new(prev_hash: u64, index_path: String) -> IndexRequest {
        IndexRequest {
            message_type: IndexRequest::messagetype().into(),
            prev_hash,
            index_path,
        }
    }
}

#[derive(Deserialize, Serialize, Clone, Debug)]
pub struct IndexResponse {
    message_type: u64,
    pub hash: u64,
    pub path_to_index_file: String,
}

impl MessageTypeTrait for IndexResponse {
    fn messagetype() -> MessageType {
        return MessageType::IndexResponse;
    }
    fn is_valid(&self) -> bool {
        return self.message_type == (Self::messagetype() as u64);
    }
}
impl IndexResponse {
    pub fn new(hash: u64, path_to_index_file: String) -> IndexResponse {
        IndexResponse {
            message_type: IndexResponse::messagetype().into(),
            hash,
            path_to_index_file,
        }
    }
    // pub fn save(&self, path: String) {
    //     let mut local_index_path = PathBuf::new();
    //     local_index_path.push(path);
    //     local_index_path.push(format!("{}.index", self.hash));
    // }
}
