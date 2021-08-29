use std::ffi::OsStr;
use std::process::Command;
use std::result::Result;


fn which(cmd: &str) -> Result<(), i32> {
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

fn find<S: AsRef<OsStr>>(item: &str, path: S) {
    if which("fd").is_ok() {
        let output = Command::new("fd")
            .arg(item)
            .arg(path)
            .output()
            .expect("Failed to find Cargo");
        println!("{}", String::from_utf8_lossy(&output.stdout));
    }
}

fn main() {
    find("Cargo", ".")
}
