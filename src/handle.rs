use std::net::TcpStream;

use crate::structs::ServerDaemon;

pub trait HandleServer {
    fn handle(&self, stream: &mut TcpStream, server_daemon: &ServerDaemon) -> Result<(), ()>;
}
