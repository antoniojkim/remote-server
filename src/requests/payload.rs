extern crate rmp_serde as rmps;
extern crate serde;

use serde::de::DeserializeOwned;
use serde::{Deserialize, Serialize};

use super::exit_request::{ExitRequest, ExitResponse};
use super::msg_request::{MsgRequest, MsgResponse};
use super::request::{Request, Response};
use super::types::PayloadType;

pub trait Encode {
    fn as_bytes(&self) -> Vec<u8>;
}

impl<T> Encode for T
where
    T: Serialize,
{
    fn as_bytes(&self) -> Vec<u8> {
        return rmps::to_vec(&self).unwrap();
    }
}

pub trait Decode<T> {
    fn from_bytes(data: &Vec<u8>) -> Result<T, rmps::decode::Error>;
}

impl<T> Decode<T> for T
where
    T: DeserializeOwned,
{
    fn from_bytes(data: &Vec<u8>) -> Result<T, rmps::decode::Error> {
        return rmps::from_slice(&data.as_slice());
    }
}

#[derive(Debug, PartialEq, Deserialize, Serialize)]
pub struct Payload {
    payload_type: PayloadType,
    data: Vec<u8>,
}

impl Payload {
    pub fn as_bytes(&self) -> Vec<u8> {
        return rmps::to_vec(&self).unwrap();
    }

    pub fn from_bytes(data: &Vec<u8>) -> Result<Payload, rmps::decode::Error> {
        return rmps::from_slice(&data.as_slice());
    }

    pub fn from_request<T>(request: &T) -> Payload
    where
        T: Request + Serialize,
    {
        Payload {
            payload_type: request.get_type(),
            data: request.as_bytes(),
        }
    }

    pub fn from_response<T>(response: &T) -> Payload
    where
        T: Response + Serialize,
    {
        Payload {
            payload_type: response.get_type(),
            data: response.as_bytes(),
        }
    }

    pub fn to_request(&self) -> Box<dyn Request> {
        match self.payload_type {
            PayloadType::Exit => Box::new(ExitRequest::from_bytes(&self.data).unwrap()),
            PayloadType::Msg => Box::new(MsgRequest::from_bytes(&self.data).unwrap()),
        }
    }

    pub fn to_response(&self) -> Box<dyn Response> {
        match self.payload_type {
            PayloadType::Exit => Box::new(ExitResponse::from_bytes(&self.data).unwrap()),
            PayloadType::Msg => Box::new(MsgResponse::from_bytes(&self.data).unwrap()),
        }
    }
}
