use pyo3::{pyclass, pymethods};
use std::sync::{Mutex, OnceLock};

#[pyclass]
pub struct WarningSink {
    quiet: bool,
    #[pyo3(get)]
    pub at_least_one_warning_issued: bool,
    records: Vec<String>,
}

#[pymethods]
impl WarningSink {
    #[new]
    pub fn new(quiet: bool) -> Self {
        Self {
            quiet,
            at_least_one_warning_issued: false,
            records: Vec::new(),
        }
    }

    pub fn __call__(&mut self, s: String) {
        self.at_least_one_warning_issued = true;
        if !self.quiet {
            self.records.push(s);
        }
    }

    pub fn flush(&self) {
        for record in &self.records {
            eprintln!("{record}");
        }
    }
}

static WARNING_SINK: OnceLock<Mutex<WarningSink>> = OnceLock::new();

pub fn warn(s: String) {
    if let Some(sink) = WARNING_SINK.get() {
        if let Ok(mut sink) = sink.lock() {
            sink.__call__(s);
        }
    }
}

pub fn flush_warnings() -> bool {
    if let Some(sink) = WARNING_SINK.get() {
        if let Ok(sink) = sink.lock() {
            sink.flush();
            return sink.at_least_one_warning_issued;
        }
    }
    false
}

pub fn register_warning_sink(sink: WarningSink) {
    let _ = WARNING_SINK.set(Mutex::new(sink));
}
