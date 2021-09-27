extern crate ssh;

use std::path::Path;

pub fn copy_from<T: AsRef<Path>>(session: ssh::Session, path: T) -> Result<(), ()> {
    Ok(())
}
