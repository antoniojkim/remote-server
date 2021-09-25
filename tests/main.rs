// use std::time::Instant;

// mod utils;

// pub use crate::utils::hash;
// pub use crate::utils::shutil;

// fn main() {
//     let result = shutil::find("Cargo", ".");
//     if result.is_ok() {
//         let mut files = result.unwrap();
//         files.sort();
//         println!("{:?}", files);
//     }
//     for i in 0..3 {
//         let now = Instant::now();

//         let result = shutil::find("", ".");
//         if result.is_ok() {
//             let mut files = result.unwrap();
//             files.sort();
//             let h = hash::hash(&files);
//             println!("{}: {}", i, h);
//         }

//         println!("Time: {} milliseconds", now.elapsed().as_millis())
//     }
// }
