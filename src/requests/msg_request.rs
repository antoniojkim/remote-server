use std::convert::From;

use super::payload::Payload;
use super::request::{Request, Response};
use super::types::PayloadType;

extern crate rmp_serde as rmps;
extern crate serde;

use serde::{Deserialize, Serialize};

#[derive(Debug, PartialEq, Deserialize, Serialize)]
pub struct MsgResponse {
    contents: String,
}

impl MsgResponse {
    pub fn new() -> MsgResponse {
        MsgResponse {
            contents: "Hello there!".to_string(),
        }
    }
}

impl Response for MsgResponse {
    fn run(&self) -> Result<u16, u16> {
        Err(1)
    }
    fn get_type(&self) -> PayloadType {
        PayloadType::MsgResponse
    }
}

#[derive(Debug, PartialEq, Deserialize, Serialize)]
pub struct MsgRequest {
    contents: String,
}

impl MsgRequest {
    pub fn new() -> MsgRequest {
        MsgRequest {
            contents: "Hiya!".to_string(),
        }
    }
}

impl Request for MsgRequest {
    fn run(&self) -> Option<Payload> {
        Some(Payload::from_response(&MsgResponse::new()))
    }
    fn get_type(&self) -> PayloadType {
        PayloadType::MsgRequest
    }
}
