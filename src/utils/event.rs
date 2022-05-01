use std::sync::{Arc, Mutex};

pub struct Event {
    value: Arc<Mutex<bool>>,
}

impl Event {
    pub fn new() -> Event {
        Event {
            value: Arc::new(Mutex::new(false)),
        }
    }

    pub fn is_set(&self) -> bool {
        let is_set = self.value.lock().unwrap();
        *is_set
    }

    pub fn set(&mut self) {
        let mut is_set = self.value.lock().unwrap();
        *is_set = true;
    }

    pub fn clear(&mut self) {
        let mut is_set = self.value.lock().unwrap();
        *is_set = false;
    }
}

impl Clone for Event {
    fn clone(&self) -> Event {
        Event {
            value: self.value.clone(),
        }
    }
}
