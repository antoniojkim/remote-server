extern crate dirs;

use std::path::PathBuf;
use std::string::String;

use clap::{App, Arg};

use std::sync::Once;

static mut DEFAULT_SERVER_PATH: String = String::new();
static INIT_BUILD_APP: Once = Once::new();

pub fn build_app() -> App<'static, 'static> {
    INIT_BUILD_APP.call_once(|| unsafe {
        let mut default_server_path = PathBuf::new();
        default_server_path.push(dirs::home_dir().unwrap());
        default_server_path.push(".emacs_remote");
        default_server_path.push("server");
        DEFAULT_SERVER_PATH = default_server_path.to_str().unwrap().to_owned();
    });

    return App::new("emacs-remote-server")
        .version("0.0.1")
        .author("antoniojkim <contact@antoniojkim.com>")
        .about("Starts emacs remote server")
        .arg(
            Arg::with_name("port")
                .short("p")
                .long("port")
                .default_value("9130")
                .help("Specifies the port to listen on"),
        )
        .arg(
            Arg::with_name("server_path")
                .short("s")
                .long("server_path")
                .default_value(unsafe { DEFAULT_SERVER_PATH.as_str() })
                .help("Path to server directory"),
        );
}
