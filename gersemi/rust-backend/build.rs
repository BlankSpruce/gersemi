use std::process::Command;

fn main() {
    let output = Command::new("cargo").arg("--version").output().unwrap();
    let version = String::from_utf8(output.stdout).unwrap();
    println!("cargo:rustc-env=CARGO_VERSION={}", version.trim());
}
