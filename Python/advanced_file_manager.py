import os
import shutil
import hashlib
from datetime import datetime

def get_file_hash(filepath, hash_algorithm='sha256'):
    hasher = hashlib.new(hash_algorithm)
    try:
        with open(filepath, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()
    except IOError as e:
        print(f"파일을 읽는 중 오류 발생: {e}")
        return None

def find_duplicate_files(directory):
    print(f"[{directory}] 디렉토리에서 중복 파일 탐색 시작...")
    file_hashes = {}
    duplicates = []
    
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            
            try:
                file_size = os.path.getsize(full_path)
                if file_size in file_hashes:
                    current_hash = get_file_hash(full_path)
                    if current_hash is not None and current_hash in file_hashes[file_size]:
                        duplicates.append((full_path, file_hashes[file_size][current_hash]))
                    else:
                        file_hashes[file_size][current_hash] = full_path
                else:
                    file_hashes[file_size] = {get_file_hash(full_path): full_path}

            except (IOError, OSError) as e:
                print(f"파일 접근 오류: {e}")
                continue

    return duplicates

def manage_duplicate_files(duplicates, action='list'):
    if not duplicates:
        print("중복 파일이 없다.")
        return

    print(f"총 {len(duplicates)}개의 중복 파일 쌍 발견.")
    
    for i, (path1, path2) in enumerate(duplicates):
        print(f"--- 중복 파일 쌍 {i+1} ---")
        print(f"원본: {path1}")
        print(f"중복: {path2}")
        
        if action == 'delete':
            try:
                os.remove(path2)
                print(f"-> 중복 파일 삭제 완료: {path2}")
            except OSError as e:
                print(f"-> 파일 삭제 중 오류 발생: {e}")
        elif action == 'move':
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            move_dir = f'duplicates_{timestamp}'
            if not os.path.exists(move_dir):
                os.makedirs(move_dir)
            try:
                shutil.move(path2, os.path.join(move_dir, os.path.basename(path2)))
                print(f"-> 중복 파일을 [{move_dir}]로 이동 완료.")
            except shutil.Error as e:
                print(f"-> 파일 이동 중 오류 발생: {e}")

if __name__ == '__main__':
    test_dir = 'test_files'
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir)
    
    with open(os.path.join(test_dir, 'file1.txt'), 'w') as f:
        f.write('Hello, world!')
    with open(os.path.join(test_dir, 'file2.txt'), 'w') as f:
        f.write('Hello, world!')
    with open(os.path.join(test_dir, 'file3.txt'), 'w') as f:
        f.write('Different content.')

    print("테스트 환경 설정 완료.")
    
    found_duplicates = find_duplicate_files(test_dir)
    
    manage_duplicate_files(found_duplicates, action='list')
    
    print("스크립트 실행 완료.")