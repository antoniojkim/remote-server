use std::ffi::OsStr;
use std::iter::FromIterator;
use std::process::{Command, Stdio};
use std::result::Result;
use std::sync::Once;

pub fn bash(cmd: String) -> Result<String, i32> {
    let output = Command::new("bash")
        .arg("-c")
        .arg(cmd)
        .stderr(Stdio::null())
        .output()
        .expect("bash command could not be executed");

    let code = output.status.code().unwrap();
    if code == 0 {
        return Ok(String::from_utf8_lossy(&output.stdout).to_string());
    }
    return Err(code);
}

pub fn which(cmd: &str) -> Result<(), i32> {
    match bash(format!("which {}", cmd)) {
        Ok(_) => Ok(()),
        Err(code) => Err(code),
    }
}

static mut FD_EXISTS: bool = false;
static mut RG_EXISTS: bool = false;
static FIND_INIT: Once = Once::new();

pub fn find(item: String, path: String) -> Result<Vec<String>, i32> {
    FIND_INIT.call_once(|| unsafe {
        FD_EXISTS = which("fd").is_ok();
        RG_EXISTS = which("rg").is_ok();
    });
    if unsafe { FD_EXISTS } {
        return match bash(format!("fd -t f {} {}", item, path)) {
            Ok(stdout) => Ok(Vec::from_iter(
                stdout.trim_end().split("\n").map(String::from),
            )),
            Err(code) => Err(code),
        };
    }
    return Err(-1);
}
