extern crate serde;

use serde::{Deserialize, Serialize};

#[derive(Debug, PartialEq, Deserialize, Serialize)]
pub enum RequestType {
    InitRequest,
}

#[derive(Debug, PartialEq, Deserialize, Serialize)]
pub enum ResponseType {
    InitResponse,
}
