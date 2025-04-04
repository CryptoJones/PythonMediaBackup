import os
import hashlib
import shutil
import logging
import sys

# Configure logging to log to a text file
logging.basicConfig(filename='directory_sync.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def hash_file(file_path):
    """Generate a hash for a single file."""
    try:
        hash_sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while chunk := f.read(4096):
                hash_sha256.update(chunk)
        """logging.info(f"Hashed file: {file_path}")
        This function has been moved to inside the hash_directory module"""
        return hash_sha256.hexdigest()
    except Exception as e:
        logging.error(f"Error hashing file {file_path}: {e}")
        raise

def hash_directory(directory_path):
    """Recursively hashes all files in a directory and its subdirectories."""
    hashes = {}
    for dirpath, _, filenames in os.walk(directory_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            try:
                file_hash = hash_file(file_path)
                logging.info(f"File hash {file_hash} generated for the following file: {file_path}")
                relative_path = os.path.relpath(file_path, directory_path)
                hashes[relative_path] = file_hash
            except Exception as e:
                logging.error(f"Error processing file {file_path}: {e}")
    logging.info(f"Completed hashing for directory: {directory_path}")
    return hashes

def copy_empty_dirs(src_dir, dst_dir):
    """Copy empty directories from src_dir to dst_dir."""
    for dirpath, dirnames, filenames in os.walk(src_dir):
        if not dirnames and not filenames:
            relative_path = os.path.relpath(dirpath, src_dir)
            dst_path = os.path.join(dst_dir, relative_path)
            if not os.path.exists(dst_path):
                os.makedirs(dst_path)
                logging.info(f"Created empty directory: {dst_path}")

def copy_new_or_different_files(src_dir, dst_dir, src_hashes, dst_hashes):
    """Copies files from src_dir to dst_dir that are either new or different."""
    for file, src_hash in src_hashes.items():
        dst_path = os.path.join(dst_dir, file)
        if not os.path.exists(dst_path) or dst_hashes.get(file) != src_hash:
            src_path = os.path.join(src_dir, file)
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            shutil.copy2(src_path, dst_path)
            logging.info(f"Copied file from {src_path} to {dst_path}")

if __name__ == '__main__':
    # Hardcoded fallback paths
    default_src = 'C:\\test1\\'
    default_dst = 'C:\\test2\\'

    # Use arguments if given, otherwise use defaults
    src_dir = sys.argv[1] if len(sys.argv) > 1 else default_src
    dst_dir = sys.argv[2] if len(sys.argv) > 2 else default_dst

    logging.info(f"Starting directory sync from {src_dir} to {dst_dir}")

    if not os.path.exists(src_dir) or not os.path.exists(dst_dir):
        logging.error("Source or destination directory does not exist.")
        sys.exit(1)

    # Create missing empty directories first
    copy_empty_dirs(src_dir, dst_dir)

    src_hashes = hash_directory(src_dir)
    dst_hashes = hash_directory(dst_dir)
    copy_new_or_different_files(src_dir, dst_dir, src_hashes, dst_hashes)

    logging.info("Directory sync completed.")