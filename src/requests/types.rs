extern crate serde;

use serde::{Deserialize, Serialize};

#[derive(Clone, Copy, Debug, PartialEq, Deserialize, Serialize)]
pub enum PayloadType {
    MsgRequest,
    MsgResponse,
}
