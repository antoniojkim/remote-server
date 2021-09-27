use std::clone::Clone;

pub use serde::{Deserialize, Serialize};

use crate::messages::messagetype::{MessageType, MessageTypeTrait};

#[derive(Deserialize, Serialize, Debug)]
pub struct LsRequest {
    message_type: u64,
    // path of the directory
    pub ls_path: String,
    // hash computed by combining directory itself and contents
    pub prev_hash: u64,
}

impl MessageTypeTrait for LsRequest {
    fn messagetype() -> MessageType {
        return MessageType::LsRequest;
    }
    fn is_valid(&self) -> bool {
        return self.message_type == (Self::messagetype() as u64);
    }
}
impl LsRequest {
    pub fn new(prev_hash: u64, index_path: String) -> LsRequest {
        LsRequest {
            message_type: LsRequest::messagetype().into(),
            prev_hash,
            index_path,
        }
    }
}

#[derive(Deserialize, Serialize, Debug)]
pub struct LsResponse {
    message_type: u64,
    pub hash: u64,
    pub path_to_index_file: String,
}

impl MessageTypeTrait for LsResponse {
    fn messagetype() -> MessageType {
        return MessageType::LsResponse;
    }
    fn is_valid(&self) -> bool {
        return self.message_type == (Self::messagetype() as u64);
    }
}
impl LsResponse {
    pub fn new(hash: u64, path_to_index_file: String) -> LsResponse {
        LsResponse {
            message_type: LsResponse::messagetype().into(),
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
