use std::thread;
use std::time::Duration;

fn main() {
    println!("Starting local daemon");
    thread::sleep(Duration::from_secs(2));
    println!("Finish local daemon");
}
