use std::process::Command;

fn main() {
    let version = match Command::new("cargo").arg("--version").output() {
        Ok(output) => match String::from_utf8(output.stdout) {
            Ok(value) => value.trim().to_string(),
            Err(_) => "cargo (unknown)".to_string(),
        },
        Err(_) => "cargo (unknown)".to_string(),
    };

    println!("cargo::rustc-env=CARGO_VERSION={version}");
}
