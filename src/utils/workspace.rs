use std::collections::hash_map::DefaultHasher;
use std::fmt;
use std::fs;
use std::hash::{Hash, Hasher};
use std::path::PathBuf;

extern crate dirs;

pub struct Workspace {
    path: PathBuf,
    project_dir: PathBuf,
    hash: u64,
}

impl Workspace {
    pub fn init(project_dir: &String) -> Workspace {
        let mut workspace = Workspace {
            path: PathBuf::new(),
            project_dir: PathBuf::from(project_dir),
            hash: 0,
        };

        let mut hasher = DefaultHasher::new();
        workspace.project_dir.hash(&mut hasher);
        workspace.hash = hasher.finish();

        workspace
            .path
            .push(dirs::home_dir().expect("Could not find home directory"));
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
    fn test_workspace_init() {
        let workspace = Workspace::init(&"project_name".to_string());
    }

    #[test]
    fn test_workspace_hashes_same() {
        let project_name = "project_name".to_string();

        let workspace1 = Workspace::init(&project_name);
        let workspace2 = Workspace::init(&project_name);

        assert_eq!(workspace1.hash, workspace2.hash);
    }
}
