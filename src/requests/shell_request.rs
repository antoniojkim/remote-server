use std::convert::{From, TryInto};
use std::io::{self, Write};
use std::path::PathBuf;
use std::process::Command;

use super::payload::Payload;
use super::request::{Request, Response};
use super::types::PayloadType;

extern crate rmp_serde as rmps;
extern crate serde;

use serde::{Deserialize, Serialize};

#[derive(Debug, PartialEq, Deserialize, Serialize)]
pub struct ShellResponse {
    status: i32,
    stdout: Vec<u8>,
    stderr: Vec<u8>,
}

impl Response for ShellResponse {
    fn run(&self) -> Result<u16, u16> {
        io::stdout().write_all(&self.stdout).unwrap();
        io::stderr().write_all(&self.stderr).unwrap();
        Ok(self.status.try_into().unwrap())
    }
    fn get_type(&self) -> PayloadType {
        PayloadType::Shell
    }
}

#[derive(Debug, PartialEq, Deserialize, Serialize)]
pub struct ShellRequest {
    project_dir: PathBuf,
    args: Vec<String>,
}

impl ShellRequest {
    pub fn new(project_dir: &PathBuf, args: Vec<String>) -> ShellRequest {
        ShellRequest {
            project_dir: project_dir.to_path_buf(),
            args,
        }
    }
}

impl Request for ShellRequest {
    fn run(&self) -> Option<Payload> {
        let output = Command::new("bash")
            .arg("-c")
            .arg(self.args.join(" "))
            .current_dir(&self.project_dir)
            .output()
            .expect("Failed to run shell command");

        Some(Payload::from_response(&ShellResponse {
            status: output.status.code().unwrap(),
            stdout: output.stdout,
            stderr: output.stderr,
        }))
    }
    fn get_type(&self) -> PayloadType {
        PayloadType::Shell
    }
}
