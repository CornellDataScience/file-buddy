import filecmp
import json
import os


def get_diff(source_dir, proposed_dir):
    differences = []

    comparison = filecmp.dircmp(source_dir, proposed_dir)
    collect_differences(comparison, differences)
    return differences


def collect_differences(comparison, differences, path=""):
    for file in comparison.left_only:
        differences.append({'type': 'deleted', 'path': os.path.join(path, file)})
    for file in comparison.right_only:
        differences.append({'type': 'added', 'path': os.path.join(path, file)})
    for file in comparison.diff_files:
        differences.append({'type': 'modified', 'path': os.path.join(path, file)})
    for subdir in comparison.common_dirs:
        collect_differences(
            comparison.subdirs[subdir],
            differences,
            os.path.join(path, subdir)
        )


def save_diff(differences):
    with open('differences.json', 'w') as f:
        json.dump(differences, f, indent=4)


if __name__ == "__main__":
    source_directory = "/path/to/your/source"
    proposed_directory = "/path/to/your/proposed"
    diffs = get_diff(source_directory, proposed_directory)
    save_diff(diffs)
