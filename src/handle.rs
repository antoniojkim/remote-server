use std::net::TcpStream;

use crate::info::ServerInfo;

pub trait Handle {
    fn handle(&self, stream: &mut TcpStream, server_info: &ServerInfo) -> Result<(), ()>;
}
