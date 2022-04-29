use super::request::{Request, Response};

extern crate rmp_serde as rmps;
extern crate serde;

use serde::{Deserialize, Serialize};

#[derive(Debug, PartialEq, Deserialize, Serialize)]
pub struct InitResponse {
    contents: String,
}

impl Response for InitResponse {
    fn run(&self) -> Result<u16, u16> {
        println!("Response: {}", self.contents);
        Ok(0)
    }

    fn as_bytes(&self) -> Vec<u8> {
        return rmps::to_vec(&self).unwrap();
    }

    // fn from_bytes(bytes: &Vec<u8>) -> Box<dyn Response> {
    //     Box::new(
    //         rmps::from_slice::<InitResponse>(bytes.as_slice()).expect("Could not convert bytes into Response")
    //     )
    // }
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
}

impl Request for InitRequest {
    fn run(&self) -> Box<dyn Response> {
        println!("Request: {}", self.contents);
        Box::new(InitResponse {
            contents: "Hiya!".to_string(),
        })
    }

    fn as_bytes(&self) -> Vec<u8> {
        return rmps::to_vec(&self).unwrap();
    }

    fn get_response_from_bytes(&self, bytes: &Vec<u8>) -> Box<dyn Response> {
        Box::new(
            rmps::from_slice::<InitResponse>(bytes.as_slice())
                .expect("Could not convert bytes into InitResponse"),
        )
    }
}
