extern crate rmp_serde as rmps;

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
