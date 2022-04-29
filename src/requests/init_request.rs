use super::request::{Dispatch, Request, Response};
use super::types::RequestType;
use super::types::ResponseType;

extern crate rmp_serde as rmps;
extern crate serde;

use serde::{Deserialize, Serialize};

#[derive(Debug, PartialEq, Deserialize, Serialize)]
pub struct InitResponse {
    contents: String,
}
impl InitResponse {
    pub fn new() -> InitResponse {
        return InitResponse {
            contents: "Hello there!".to_string(),
        };
    }

    pub fn from_bytes(data: &Vec<u8>) -> InitResponse {
        return rmps::from_slice(&data.as_slice()).unwrap();
    }

    pub fn as_response(&self) -> Response {
        Response::init(ResponseType::InitResponse, rmps::to_vec(&self).unwrap())
    }
}

impl Dispatch for InitResponse {
    fn dispatch(&self) -> Result<u16, u16> {
        Ok(0)
    }
}

#[derive(Debug, PartialEq, Deserialize, Serialize)]
pub struct InitRequest {
    contents: String,
}

impl InitRequest {
    pub fn new() -> InitRequest {
        return InitRequest {
            contents: "Hello there!".to_string(),
        };
    }

    pub fn from_bytes(data: &Vec<u8>) -> InitRequest {
        return rmps::from_slice(&data.as_slice()).unwrap();
    }

    pub fn as_request(&self) -> Request {
        Request::init(RequestType::InitRequest, rmps::to_vec(&self).unwrap())
    }
}

impl Dispatch for InitRequest {
    fn dispatch(&self) -> Result<u16, u16> {
        Ok(0)
    }
}
