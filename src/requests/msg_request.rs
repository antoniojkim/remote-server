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
        println!("Response: {}", self.contents);
        Ok(0)
    }
    fn get_type(&self) -> PayloadType {
        PayloadType::Msg
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
        println!("Request: {}", self.contents);
        Some(Payload::from_response(&MsgResponse::new()))
    }
    fn get_type(&self) -> PayloadType {
        PayloadType::Msg
    }
}
