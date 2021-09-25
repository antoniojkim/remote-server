use std::env;
use std::path::PathBuf;

use clap::{App, Arg};

use emacs_remote::structs::client::ClientDaemon;
use emacs_remote::version::VERSION;

fn main() {
    // Set up default client path
    let mut default_client_path = PathBuf::new();
    default_client_path.push(dirs::home_dir().unwrap());
    default_client_path.push(".emacs_remote");
    default_client_path.push("server");

    let app = App::new("emacs-remote-client-daemon")
        .version(VERSION)
        .author("antoniojkim <contact@antoniojkim.com>")
        .about("Starts emacs remote client daemon")
        .arg(
            Arg::with_name("workspace")
                .short("w")
                .long("workspace")
                .help("Specifies the workspace to monitor"),
        )
        .arg(
            Arg::with_name("server_port")
                .short("sp")
                .long("server_port")
                .default_value("9130")
                .help("Specifies the port that the server is listening on"),
        )
        .arg(
            Arg::with_name("client_port")
                .short("cp")
                .long("client_port")
                .default_value("9131")
                .help("Specifies the port that the client will listen on"),
        )
        .arg(
            Arg::with_name("client_path")
                .short("p")
                .long("client_path")
                .default_value(default_client_path.to_str().unwrap())
                .help("Path to client directory"),
        );

    let matches = app.get_matches_from(env::args_os());

    let mut client_daemon = ClientDaemon::new(
        matches.value_of("workspace").unwrap().to_string(),
        matches.value_of("client_path").unwrap().to_string(),
        matches.value_of("client_port").unwrap().to_string(),
        matches.value_of("server_port").unwrap().to_string(),
    );

    client_daemon.listen();
}
