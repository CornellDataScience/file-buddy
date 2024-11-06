import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import logging

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ChangeHandler(FileSystemEventHandler):
    def on_created(self, event):
        LOGGER.info(f'File {event.src_path} has been created')

    def on_modified(self, event):
        LOGGER.info(f'File {event.src_path} has been modified')

    def on_deleted(self, event):
        LOGGER.info(f'File {event.src_path} has been deleted')
        
def iterate_files(path):
    for root, dirs, files in os.walk(path):
        for file in files:
            # rename file named wow.txt to wow2.txt
            if file == 'wow.txt':
                os.rename(os.path.join(root, file), os.path.join(root, 'wow2.txt'))
                LOGGER.info(f'File {file} has been renamed to wow2.txt')

if __name__ == "__main__":
    LOGGER.info("Starting file monitor ...")

    path = os.getenv('MONITOR_DIR')
    event_handler = ChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    iterate_files(path)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
