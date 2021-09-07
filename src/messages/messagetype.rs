use num_enum::{IntoPrimitive, TryFromPrimitive};

#[derive(IntoPrimitive, TryFromPrimitive, Eq, PartialEq, Debug)]
#[repr(u64)]
pub enum MessageType {
    IndexRequest,
    IndexResponse,
}
