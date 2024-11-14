import os
import shutil


def organize_files(source_dir, target_dir):
    # TODO: Implement organization logic
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.endswith('.txt'):
                dest_dir = os.path.join(target_dir, 'TextFiles')
                os.makedirs(dest_dir, exist_ok=True)
                shutil.copy2(os.path.join(root, file), dest_dir)


if __name__ == "__main__":
    source_directory = "/data/source"
    target_directory = "/data/proposed"
    organize_files(source_directory, target_directory)
