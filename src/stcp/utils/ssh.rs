use std::{
    fs,
    io::Read,
    net::TcpStream,
    process::{Command, Stdio},
};

use ssh2::Session;
use ssh_config::SSHConfig;

pub struct SSHSession {
    host: String,
    session: Option<ssh2::Session>,
}
pub enum SSHErrorCode {
    AgentError,
    FileNotFound,
    PubKeyAuthenticationDisabled,
    AuthenticationFailed,
}

impl SSHSession {
    pub fn new(host: String) -> Result<SSHSession, SSHErrorCode> {
        let mut session = SSHSession {
            host,
            session: (None),
        };
        match session.reset() {
            Ok(()) => Ok(session),
            Err(e) => Err(e),
        }
    }

    pub fn reset(&mut self) -> Result<(), SSHErrorCode> {
        // ssh-add
        // run ssh-add if no identities found
        let status = Command::new("bash")
            .arg("-c")
            .arg("ssh-add -l; if [ $? -ne 0 ]; then ssh-add; fi")
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .status()
            .expect("failed to execute process");

        if status.code().unwrap() != 0 {
            return Err(SSHErrorCode::AgentError);
        }

        // Connect to the SSH server
        let tcp = TcpStream::connect(format!("{}:22", self.host)).unwrap();
        let mut sess = Session::new().unwrap();
        sess.set_tcp_stream(tcp);
        sess.handshake().unwrap();

        if self.host == "localhost" {
            let username = whoami::username();

            // Try to authenticate with the first identity in the agent.
            sess.userauth_agent(&username).unwrap();
        } else {
            // Parse ~/.ssh/config
            let mut ssh_config_path = dirs::home_dir().expect("Could not find home dir");
            ssh_config_path.push(".ssh");
            ssh_config_path.push("config");

            if !ssh_config_path.exists() {
                return Err(SSHErrorCode::FileNotFound);
            }

            let ssh_config =
                fs::read_to_string(ssh_config_path).expect("Could not read ~/.ssh/config");
            let ssh_config =
                SSHConfig::parse_str(&ssh_config).expect("Could not parse ~/.ssh/config");

            let host = ssh_config.query(self.host.clone());
            if host["PubKeyAuthentication"] != "yes" {
                return Err(SSHErrorCode::PubKeyAuthenticationDisabled);
            }
            let username = host["User"].to_string();

            // Try to authenticate with the first identity in the agent.
            sess.userauth_agent(&username).unwrap();
        }

        // Make sure we succeeded
        if !sess.authenticated() {
            return Err(SSHErrorCode::AuthenticationFailed);
        }

        self.session = Some(sess);

        Ok(())
    }

    pub fn shell(&mut self, cmd: &str) -> (i32, String) {
        if self.session.is_none() {
            let result = self.reset();
            assert!(result.is_ok());
            assert!(self.session.is_some());
        }
        let mut channel = self.session.as_ref().unwrap().channel_session().unwrap();
        channel.exec(cmd).unwrap();
        let mut s = String::new();
        channel.read_to_string(&mut s).unwrap();
        assert!(channel.wait_close().is_ok());

        (channel.exit_status().unwrap(), s)
    }
}
