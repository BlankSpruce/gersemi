use pyo3::{pyclass, pymethods, PyResult};
use rusqlite::{params, Connection};
use std::collections::HashMap;
use std::path::{Path, PathBuf};
use std::str::FromStr;
use std::sync::Mutex;
use std::time::UNIX_EPOCH;

#[pyclass]
pub struct Cache {
    connection: Option<Mutex<Connection>>,
}

fn file_entry(file: &Path) -> PyResult<(&str, i64, i64)> {
    let metadata = std::fs::metadata(file)?;
    let name = file.to_str().unwrap_or("---");
    let size = i64::try_from(metadata.len())?;
    let modification_time =
        i64::try_from(metadata.modified()?.duration_since(UNIX_EPOCH)?.as_nanos())?;
    Ok((name, size, modification_time))
}

fn store_file_entries(connection: &Connection, files: &[PathBuf]) {
    let Ok(mut statement) = connection.prepare("INSERT OR REPLACE INTO files VALUES (?, ?, ?)")
    else {
        return;
    };

    for file in files {
        if let Ok((name, size, modification_time)) = file_entry(file) {
            let _ = statement.execute(params![name, size, modification_time]);
        }
    }
}

fn store_configuration_summary(
    connection: &Connection,
    configuration_summary: &str,
    files: &[PathBuf],
) {
    let Ok(mut statement) = connection.prepare("INSERT OR REPLACE INTO formatted VALUES (?, ?)")
    else {
        return;
    };

    for file in files {
        let name = file.to_str().unwrap_or("---");
        let _ = statement.execute(params![name, configuration_summary]);
    }
}

fn get_files(
    connection: &Connection,
    configuration_summary: &str,
) -> HashMap<PathBuf, (usize, usize)> {
    let Ok(mut statement) = connection.prepare(
        "
        SELECT *
        FROM files
        WHERE files.path IN (
            SELECT formatted.path
            FROM formatted
            WHERE formatted.configuration_summary = (?)
        )",
    ) else {
        return HashMap::default();
    };

    let Ok(values) = statement.query_map(params![configuration_summary], |row| {
        Ok((
            row.get::<usize, String>(0)?,
            row.get::<usize, i64>(1)?,
            row.get::<usize, i64>(2)?,
        ))
    }) else {
        return HashMap::default();
    };

    let mut result = HashMap::<PathBuf, (usize, usize)>::new();
    for value in values {
        let Ok((path, size, modification_time)) = value else {
            continue;
        };
        let Ok(path) = PathBuf::from_str(&path);
        result.insert(
            path,
            (
                usize::try_from(size).unwrap(),
                usize::try_from(modification_time).unwrap(),
            ),
        );
    }
    result
}

fn create_connection(enable_cache: bool, cache_path: PathBuf) -> Option<Connection> {
    if !enable_cache {
        return None;
    }

    let Ok(connection) = Connection::open(cache_path) else {
        return None;
    };
    let Ok(_) = connection.execute("PRAGMA foreign_keys = 1", []) else {
        return None;
    };
    let Ok(_) = connection.execute(
        "
        CREATE TABLE IF NOT EXISTS files (
            path TEXT PRIMARY KEY,
            size INTEGER NOT NULL,
            modification_time INTEGER NOT NULL
        )",
        [],
    ) else {
        return None;
    };
    let Ok(_) = connection.execute(
        "
        CREATE TABLE IF NOT EXISTS formatted (
            path TEXT PRIMARY KEY,
            configuration_summary TEXT NOT NULL,
            FOREIGN KEY (path) REFERENCES files (path)
        )",
        [],
    ) else {
        return None;
    };

    Some(connection)
}

#[pymethods]
impl Cache {
    #[new]
    pub fn new(enable_cache: bool, cache_path: PathBuf) -> Self {
        Self {
            connection: create_connection(enable_cache, cache_path).map(Mutex::new),
        }
    }

    #[allow(clippy::needless_pass_by_value)]
    pub fn store_files(&self, configuration_summary: &str, files: Vec<PathBuf>) {
        let Some(ref connection) = self.connection else {
            return;
        };

        let Ok(connection) = connection.lock() else {
            return;
        };

        store_file_entries(&connection, &files);
        store_configuration_summary(&connection, configuration_summary, &files);
    }

    pub fn get_files(&self, configuration_summary: &str) -> HashMap<PathBuf, (usize, usize)> {
        let Some(ref connection) = self.connection else {
            return HashMap::default();
        };

        let Ok(connection) = connection.lock() else {
            return HashMap::default();
        };

        get_files(&connection, configuration_summary)
    }
}
