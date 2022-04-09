use std::env;
use std::path::PathBuf;
use std::thread::sleep;
use std::time::Duration;

use clap::{App, Arg};

use emacs_remote::structs::client::ClientDaemon;
use emacs_remote::version::VERSION;

fn main() {
    // Set up default emacs_remote path
    let mut default_path = PathBuf::new();
    default_path.push(dirs::home_dir().unwrap());
    default_path.push(".emacs_remote");

    let app = App::new("emacs-remote-client-daemon")
        .version(VERSION)
        .author("antoniojkim <contact@antoniojkim.com>")
        .about("Starts emacs remote client daemon")
        .arg(
            Arg::with_name("host")
                .long("host")
                .takes_value(true)
                .required(true)
                .help("Specifies the remote host to connect to. Host must exist in ~/.ssh/config"),
        )
        .arg(
            Arg::with_name("workspace")
                .short("w")
                .long("workspace")
                .takes_value(true)
                .required(true)
                .help("Specifies the path to workspace on the remote server"),
        )
        .arg(
            Arg::with_name("emacs_remote_path")
                .short("r")
                .long("emacs_remote_path")
                .default_value(default_path.to_str().unwrap())
                .help("Path to emacs-remote directory"),
        )
        .arg(
            Arg::with_name("daemon")
                .short("d")
                .long("daemon")
                .required(false)
                .takes_value(false)
                .help("If true, starts the --daemon"),
        );

    let matches = app.get_matches_from(env::args_os());

    if matches.is_present("daemon") {
        let mut client_daemon = ClientDaemon::new(
            matches.value_of("host").unwrap().to_string(),
            matches.value_of("workspace").unwrap().to_string(),
            matches.value_of("emacs_remote_path").unwrap().to_string(),
        )
        .expect("Unable to create client daemon");

        client_daemon.init();
        println!("Client Daemon Initialized!");

        client_daemon.listen();
    } else {
        // handle request case here
    }

    // for i in 1..10 {
    //     client_daemon.shell("ls -al | tail -n +2 | awk '{print $1\" \"$NF}'");
    // }
}
