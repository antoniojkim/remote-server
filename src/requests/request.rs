// extern crate serde;
// extern crate rmp_serde as rmps;

// use serde::{Deserialize, Serialize};

pub trait Response {
    fn run(&self) -> Result<u16, u16>;

    fn as_bytes(&self) -> Vec<u8>;
}

pub trait Request {
    fn run(&self) -> Box<dyn Response>;

    fn as_bytes(&self) -> Vec<u8>;

    fn get_response_from_bytes(&self, bytes: &Vec<u8>) -> Box<dyn Response>;
}

// pub trait EncodeDecode<T> {
//     fn as_bytes(&self) -> Vec<u8>;
//     fn from_bytes(bytes: &Vec<u8>) -> T;
// }

// impl<T> EncodeDecode for T where T: Response + Serialize {
//     fn as_bytes(&self) -> Vec<u8> {
//         rmps::to_vec(&self).unwrap()
//     }

//     fn from_bytes<T>(bytes: &Vec<u8>) -> T where T: Deserialize {

//     }
// }
