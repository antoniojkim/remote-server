extern crate rmp_serde as rmps;

use num_enum::{IntoPrimitive, TryFromPrimitive};

#[derive(IntoPrimitive, TryFromPrimitive, Eq, PartialEq, Debug)]
#[repr(u64)]
pub enum MessageType {
    // To test basic ping
    PingRequest,
    PingResponse,
    // For getting shell output from server
    ShellRequest,
    // Response containing a path
    PathResponse,

    // Projectile commands
    ProjectileInvalidCacheRequest,
    IndexRequest,
    IndexResponse,
}

pub trait MessageTypeTrait {
    fn messagetype() -> MessageType;
    fn is_valid(&self) -> bool;
}
