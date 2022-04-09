extern crate rmp_serde as rmps;

use std::convert::TryFrom;
use std::io::Read;
use std::io::Write;
use std::net::TcpStream;

use serde::de::DeserializeOwned;
use serde::Serialize;

use crate::messages::messagetype::{MessageType, MessageTypeTrait};

pub fn send<T: Serialize>(stream: &mut TcpStream, message: &T) -> Result<(), ()> {
    let buffer = rmps::encode::to_vec(&message).unwrap();
    if stream.write(&buffer).is_err() {
        return Err(());
    }
    if stream.flush().is_err() {
        return Err(());
    }
    Ok(())
}

pub fn recv<T>(stream: &mut TcpStream) -> Result<T, ()>
where
    T: DeserializeOwned + MessageTypeTrait,
{
    let mut buf = [0; 1024];
    stream.read(&mut buf).unwrap();

    let value: rmpv::Value = rmps::decode::from_read_ref(&buf).unwrap();
    println!("Request: {}", serde_json::to_string(&value).unwrap());

    if !value.is_array() || !value[0].is_u64() {
        return Err(());
    }
    let msgtype = MessageType::try_from(value[0].as_u64().unwrap()).unwrap();
    if msgtype != T::messagetype() {
        return Err(());
    }

    let result: T = rmp_serde::from_read_ref(&buf).unwrap();
    if !result.is_valid() {
        return Err(());
    }

    return Ok(result);
}
