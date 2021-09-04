use std::ffi::OsStr;
use std::iter::FromIterator;
use std::process::Command;
use std::result::Result;
use std::sync::Once;

pub fn which(cmd: &str) -> Result<(), i32> {
    let output = Command::new("which")
        .arg(cmd)
        .output()
        .expect("which could not be executed");

    let code = output.status.code().unwrap();
    if code == 0 {
        return Ok(());
    }
    return Err(code);
}

static mut FD_EXISTS: bool = false;
static mut RG_EXISTS: bool = false;
static FIND_INIT: Once = Once::new();

pub fn find<S: AsRef<OsStr>>(item: S, path: S) -> Result<Vec<String>, i32> {
    FIND_INIT.call_once(|| unsafe {
        FD_EXISTS = which("fd").is_ok();
        RG_EXISTS = which("rg").is_ok();
    });
    if unsafe { FD_EXISTS } {
        let output = Command::new("fd")
            .arg("-t")
            .arg("f")
            .arg(item)
            .arg(path)
            .output()
            .expect("Failed to find Cargo");

        let code = output.status.code().unwrap();
        if code == 0 {
            return Ok(Vec::from_iter(
                String::from_utf8_lossy(&output.stdout)
                    .to_string()
                    .trim_end()
                    .split("\n")
                    .map(String::from),
            ));
        }
        return Err(code);
    }
    return Err(-1);
}
