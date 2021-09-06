pub(crate) use serde::{Deserialize, Serialize};

use super::messagetype::MessageType;

#[derive(Deserialize, Serialize, Debug)]
pub struct IndexRequest {
    pub message_type: u64,
    pub prev_hash: u64,
    pub index_path: String,
}

impl IndexRequest {
    pub fn new(prev_hash: u64, index_path: String) -> IndexRequest {
        IndexRequest {
            message_type: MessageType::IndexRequest as u64,
            prev_hash,
            index_path,
        }
    }
}

#[derive(Deserialize, Serialize, Debug)]
pub struct IndexResponse {
    pub message_type: u64,
    pub hash: u64,
}

impl IndexResponse {
    pub fn new(hash: u64) -> IndexResponse {
        IndexResponse {
            message_type: MessageType::IndexResponse as u64,
            hash,
        }
    }
}
