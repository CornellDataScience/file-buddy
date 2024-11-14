import os
from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import FileSystemEventHandler
import time
import logging
from file_renamer import FileRenameHandler

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Example naming request - in production this should come from some sort of user interface
NAMING_REQUEST = "I want the files in this folder to be called homework then an underscore then the number of the homework"

class ChangeHandler(FileSystemEventHandler):
    def __init__(self, renamer: FileRenameHandler):
        super().__init__()
        self.renamer = renamer
        
    def on_created(self, event):
        LOGGER.info(f'File {event.src_path} has been created')

    def on_modified(self, event):
        LOGGER.info(f'File {event.src_path} has been modified')

    def on_deleted(self, event):
        LOGGER.info(f'File {event.src_path} has been deleted')

def process_initial_rename(path: str, renamer: FileRenameHandler):
    """Process initial rename of existing files in the directory."""
    try:
        name_mappings = renamer.process_rename_request(path, NAMING_REQUEST)
        renamer.apply_rename(path, name_mappings)
        LOGGER.info("Initial file rename completed successfully")
    except Exception as e:
        LOGGER.error(f"Error in initial rename: {e}")
        
# def iterate_files(path):
#     for root, dirs, files in os.walk(path):
#         for file in files:
#             # rename file named wow.txt to wow2.txt
#             if file == 'wow.txt':
#                 os.rename(os.path.join(root, file), os.path.join(root, 'wow2.txt'))
#                 LOGGER.info(f'File {file} has been renamed to wow2.txt')

if __name__ == "__main__":
    LOGGER.info("Starting file monitor ...")


    path = os.getenv('MONITOR_DIR')
    api_key = os.getenv('OPENAI_API_KEY')

    if not api_key:
        LOGGER.error("OPENAI_API_KEY environment variable is not set!")
        LOGGER.error("Please set OPENAI_API_KEY in your .env file and ensure it's being passed to the container")
        exit(1)

    if not path:
        LOGGER.error("MONITOR_DIR environment variable is not set!")
        exit(1)

    try:
        renamer = FileRenameHandler()
        process_initial_rename(path, renamer)
        event_handler = ChangeHandler(renamer)
        observer = Observer()
        observer.schedule(event_handler, path, recursive=True)
        observer.start()

        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()
    except Exception as e:
        LOGGER.error(f"An error occurred: {e}")
        exit(1)