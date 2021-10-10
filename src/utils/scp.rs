extern crate ssh2;

use std::path::Path;

pub fn copy_from<T: AsRef<Path>>(session: ssh2::Session, path: T) -> Result<(), ()> {
    Ok(())
}
