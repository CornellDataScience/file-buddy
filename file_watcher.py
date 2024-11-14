import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess


class ChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        # Trigger Docker container to reorganize folders
        subprocess.run([
            'docker', 'run', '--rm',
            '-v', '/path/to/your/source:/data/source',
            '-v', '/path/to/your/proposed:/data/proposed',
            'your_docker_image_name'
        ])
        # Generate differences after Docker container runs
        subprocess.run(['python', 'generate_diff.py'])


if __name__ == "__main__":
    path = "/path/to/your/source"
    event_handler = ChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path=path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
