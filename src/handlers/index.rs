use super::super::handle::Handle;
use super::super::messages::index::IndexRequest;

impl Handle for IndexRequest {
    fn handle(&self) {
        println!("IndexRequest: {:?}", self);
    }
}
