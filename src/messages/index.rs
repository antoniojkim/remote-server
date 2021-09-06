pub(crate) use serde::{Deserialize, Serialize};

#[derive(Deserialize, Serialize, Debug)]
pub struct IndexMessageRequest {
    pub prev_hash: u64,
    pub index_path: String,
}

#[derive(Deserialize, Serialize, Debug)]
pub struct IndexMessageResponse {
    pub hash: u64,
}
