pub struct DropGuard<'a> {
    f: &'a dyn Fn(),
}

impl<'a> DropGuard<'a> {
    pub fn new(f: &'a dyn Fn()) -> Self {
        Self { f }
    }
}

impl<'a> Drop for DropGuard<'a> {
    fn drop(&mut self) {
        (self.f)();
    }
}
