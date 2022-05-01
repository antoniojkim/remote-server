extern crate rmp_serde as rmps;
extern crate serde;

use serde::de::DeserializeOwned;
use serde::{Deserialize, Serialize};

use super::payload::Payload;
use super::types::PayloadType;

pub trait Response {
    fn run(&self) -> Result<u16, u16>;
    fn get_type(&self) -> PayloadType;
}

pub trait Request {
    fn run(&self) -> Option<Payload>;
    fn get_type(&self) -> PayloadType;
}
