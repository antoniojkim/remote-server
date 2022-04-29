extern crate rmp_serde as rmps;
extern crate serde;

use serde::{Deserialize, Serialize};

use super::types::{RequestType, ResponseType};

#[derive(Debug, PartialEq, Deserialize, Serialize)]
pub struct Request {
    r#type: RequestType,
    data: Vec<u8>,
}

impl Request {
    pub fn new(r#type: RequestType, size: usize) -> Request {
        Request {
            r#type,
            data: Vec::with_capacity(size),
        }
    }

    pub fn init(r#type: RequestType, data: Vec<u8>) -> Request {
        Request { r#type, data }
    }

    pub fn r#type(&self) -> &RequestType {
        &self.r#type
    }

    pub fn data(&self) -> &Vec<u8> {
        &self.data
    }

    pub fn as_bytes(&self) -> Vec<u8> {
        return rmps::to_vec(&self).unwrap();
    }

    pub fn from_bytes(bytes: &Vec<u8>) -> Result<Response, rmps::decode::Error> {
        return rmps::from_slice(&bytes.as_slice());
    }
}

#[derive(Debug, PartialEq, Deserialize, Serialize)]
pub struct Response {
    r#type: ResponseType,
    data: Vec<u8>,
}

impl Response {
    pub fn new(r#type: ResponseType, size: usize) -> Response {
        Response {
            r#type,
            data: Vec::with_capacity(size),
        }
    }

    pub fn init(r#type: ResponseType, data: Vec<u8>) -> Response {
        Response { r#type, data }
    }

    pub fn r#type(&self) -> &ResponseType {
        &self.r#type
    }

    pub fn data(&self) -> &Vec<u8> {
        &self.data
    }

    pub fn as_bytes(&self) -> Vec<u8> {
        return rmps::to_vec(&self).unwrap();
    }

    pub fn from_bytes(bytes: &Vec<u8>) -> Result<Request, rmps::decode::Error> {
        return rmps::from_slice(&bytes.as_slice());
    }
}

pub trait Dispatch {
    fn dispatch(&self) -> Result<u16, u16>;
}
