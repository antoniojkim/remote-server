extern crate rmp_serde as rmps;

use std::convert::TryFrom;
use std::io::Read;
use std::net::TcpStream;

use num_enum::{IntoPrimitive, TryFromPrimitive};

#[derive(IntoPrimitive, TryFromPrimitive, Eq, PartialEq, Debug)]
#[repr(u64)]
pub enum MessageType {
    IndexRequest,
    IndexResponse,
}

pub trait MessageTypeTrait {
    fn messagetype() -> MessageType;
    fn is_valid(&self) -> bool;
}
