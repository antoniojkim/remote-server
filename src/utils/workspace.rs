use std::collections::hash_map::DefaultHasher;
use std::fmt;
use std::fs;
use std::hash::{Hash, Hasher};
use std::net::SocketAddr;
use std::path::PathBuf;

extern crate dirs;

pub struct Workspace {
    path: PathBuf,
    project_dir: PathBuf,
    hash: u64,
}

impl Workspace {
    pub fn new(project_dir: &String) -> Workspace {
        let mut workspace = Workspace {
            path: PathBuf::new(),
            project_dir: PathBuf::from(project_dir),
            hash: 0,
        };

        let mut hasher = DefaultHasher::new();
        workspace.project_dir.hash(&mut hasher);
        workspace.hash = hasher.finish();

        let home_dir = dirs::home_dir().expect("Could not find home directory");
        workspace.path.push(home_dir);
        workspace.path.push(".emacs-remote-server");
        workspace.path.push("workspaces");
        workspace.path.push(
            workspace
                .project_dir
                .file_name()
                .expect("Invalid Project Name"),
        );

        if !workspace.path.exists() {
            fs::create_dir_all(&workspace.path).expect("Could not make workspace path");
        }

        return workspace;
    }

    pub fn daemon_addr(&self) -> Option<SocketAddr> {
        let mut daemon_port_file = self.path.clone();
        daemon_port_file.push("daemon.port");

        if daemon_port_file.exists() {
            let daemon_port =
                fs::read_to_string(daemon_port_file).expect("Unable to read daemon file");
            return Some(SocketAddr::from((
                [127, 0, 0, 1],
                daemon_port.parse::<u16>().unwrap(),
            )));
        }

        None
    }

    pub fn path(&self) -> &PathBuf {
        return &self.path;
    }
}

impl fmt::Display for Workspace {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "Workspace({}, {})", self.path.display(), self.hash)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_workspace_new() {
        let project_name = "project_name".to_string();
        let workspace = Workspace::new(&project_name);

        assert_eq!(workspace.project_dir.to_str().unwrap(), project_name);
    }

    #[test]
    fn test_workspace_hashes_same() {
        let project_name = "project_name".to_string();

        let workspace1 = Workspace::new(&project_name);
        let workspace2 = Workspace::new(&project_name);

        assert_eq!(workspace1.project_dir.to_str().unwrap(), project_name);
        assert_eq!(workspace2.project_dir.to_str().unwrap(), project_name);

        assert_eq!(workspace1.hash, workspace2.hash);

        assert!(workspace1.path.exists());
        assert!(workspace1.path.is_dir());
    }
}
