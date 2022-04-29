use super::init_request::{InitRequest, InitResponse};
use super::request::{Dispatch, Request, Response};
use super::types::{RequestType, ResponseType};

impl Dispatch for Request {
    fn dispatch(&self) -> Result<u16, u16> {
        match self.r#type() {
            RequestType::InitRequest => InitRequest::from_bytes(self.data()).dispatch(),
            _ => Err(1),
        }
    }
}

impl Dispatch for Response {
    fn dispatch(&self) -> Result<u16, u16> {
        match self.r#type() {
            ResponseType::InitResponse => InitResponse::from_bytes(self.data()).dispatch(),
            _ => Err(1),
        }
    }
}
