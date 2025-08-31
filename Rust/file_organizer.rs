use std::fs::{self, metadata, read_dir};
use std::path::{Path, PathBuf};
use std::io::{self, Write};
use std::collections::HashMap;
use std::hash::{Hasher, DefaultHasher};
use std::time::SystemTime;

/// 주어진 경로에 있는 파일을 정리하고, 중복 파일이나 오래된 파일을 처리합니다.
fn organize_files(source_dir: &Path, dry_run: bool) -> io::Result<()> {
    if !source_dir.exists() || !source_dir.is_dir() {
        println!("Error: The source directory does not exist or is not a directory.");
        return Ok(());
    }

    println!("--- File Organizer Started ---");
    if dry_run {
        println!("*** Dry Run Mode Enabled: No files will be moved or deleted. ***");
    }

    let mut file_map: HashMap<u64, Vec<PathBuf>> = HashMap::new();
    let mut deleted_count = 0;
    let mut moved_count = 0;

    // 1. 디렉토리를 순회하며 파일 해시맵을 생성
    println!("Scanning files for duplicates...");
    for entry in read_dir(source_dir)? {
        let entry = entry?;
        let path = entry.path();
        if path.is_file() {
            let file_meta = metadata(&path)?;
            if file_meta.len() > 0 {
                let mut hasher = DefaultHasher::new();
                let file_content = fs::read(&path)?;
                hasher.write(&file_content);
                let file_hash = hasher.finish();
                file_map.entry(file_hash).or_insert_with(Vec::new).push(path.clone());
            }
        }
    }

    // 2. 중복 파일 삭제 (하나의 원본을 제외하고)
    println!("Checking for duplicate files...");
    for (_hash, paths) in file_map.iter_mut() {
        if paths.len() > 1 {
            println!("\nFound duplicates for hash {:x}", _hash);
            let original = paths.remove(0);
            println!("- Keeping original: {}", original.display());

            for duplicate in paths.iter() {
                println!("- Deleting duplicate: {}", duplicate.display());
                if !dry_run {
                    fs::remove_file(duplicate)?;
                    deleted_count += 1;
                }
            }
        }
    }
    println!("Found and processed {} duplicate files.", deleted_count);
    
    // 3. 오래된 파일 정리 (1년 이상 수정되지 않은 파일)
    println!("\nChecking for old files (older than 1 year)...");
    let now = SystemTime::now();
    let one_year_ago = now - std::time::Duration::from_secs(365 * 24 * 60 * 60);
    
    let old_files_dir = source_dir.join("old_files");
    if !old_files_dir.exists() {
        if !dry_run {
            fs::create_dir(&old_files_dir)?;
            println!("Created directory for old files: {}", old_files_dir.display());
        } else {
            println!("Would create directory for old files: {}", old_files_dir.display());
        }
    }

    let mut entries_to_process = Vec::new();
    for entry in read_dir(source_dir)? {
        let entry = entry?;
        let path = entry.path();
        entries_to_process.push(path);
    }
    
    for path in entries_to_process {
        if path.is_file() {
            if let Ok(file_meta) = metadata(&path) {
                if let Ok(modified_time) = file_meta.modified() {
                    if modified_time < one_year_ago {
                        if !dry_run {
                            let new_path = old_files_dir.join(path.file_name().unwrap());
                            println!("Moving old file: {} -> {}", path.display(), new_path.display());
                            fs::rename(&path, &new_path)?;
                            moved_count += 1;
                        } else {
                            println!("Would move old file: {}", path.display());
                        }
                    }
                }
            }
        }
    }
    println!("Found and processed {} old files.", moved_count);

    println!("\n--- File Organizer Finished ---");
    Ok(())
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let mut source_dir = PathBuf::new();
    let mut dry_run = false;

    // 명령줄 인자 파싱
    if args.len() < 2 {
        println!("Usage: {} <directory> [--dry-run]", args[0]);
        return;
    }

    source_dir.push(&args[1]);

    if args.len() > 2 && args[2] == "--dry-run" {
        dry_run = true;
    }

    // 파일 정리 함수 실행
    if let Err(e) = organize_files(&source_dir, dry_run) {
        eprintln!("An error occurred: {}", e);
    }
}