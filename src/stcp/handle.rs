use std::net::TcpStream;

use crate::structs::client::ClientDaemon;
use crate::structs::server::ServerDaemon;

pub trait HandleClientDaemon {
    fn handle(&self, stream: &mut TcpStream, client_daemon: &mut ClientDaemon) -> Result<(), ()>;
}

pub trait HandleServerDaemon {
    fn handle(&self, stream: &mut TcpStream, server_daemon: &mut ServerDaemon) -> Result<(), ()>;
}
