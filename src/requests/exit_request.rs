use std::convert::From;

use super::payload::Payload;
use super::request::{Request, Response};
use super::types::PayloadType;

extern crate rmp_serde as rmps;
extern crate serde;

use serde::{Deserialize, Serialize};

#[derive(Debug, PartialEq, Deserialize, Serialize)]
pub struct ExitResponse {
    status: u16,
}

impl ExitResponse {
    pub fn new(status: u16) -> ExitResponse {
        ExitResponse { status }
    }
}

impl Response for ExitResponse {
    fn run(&self) -> Result<u16, u16> {
        if self.status != 0 {
            println!("Error exiting with code: {}", self.status);
            return Err(self.status);
        }
        Ok(self.status)
    }
    fn get_type(&self) -> PayloadType {
        PayloadType::Exit
    }
}

#[derive(Debug, PartialEq, Deserialize, Serialize)]
pub struct ExitRequest {}

impl ExitRequest {
    pub fn new() -> ExitRequest {
        ExitRequest {}
    }
}

impl Request for ExitRequest {
    fn run(&self) -> Option<Payload> {
        Some(Payload::from_response(&ExitResponse::new(0)))
    }
    fn get_type(&self) -> PayloadType {
        PayloadType::Exit
    }
}
