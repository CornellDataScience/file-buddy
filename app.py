# app.py
import os
from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import FileSystemEventHandler
import time
import logging
from context_enhanced_renamer import ContextEnhancedRenamer

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Example naming request - in production this should come from some sort of user interface
NAMING_REQUEST = "Name files based on their main topic or subject matter"

class ChangeHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.context_renamer = ContextEnhancedRenamer()
        
    def on_created(self, event):
        LOGGER.info(f'File {event.src_path} has been created')

    def on_modified(self, event):
        LOGGER.info(f'File {event.src_path} has been modified')

    def on_deleted(self, event):
        LOGGER.info(f'File {event.src_path} has been deleted')

def process_initial_rename(path: str, renamer: ContextEnhancedRenamer):
    """Process initial rename of existing files in the directory."""
    try:
        name_mappings = renamer.process_context_aware_rename(path, NAMING_REQUEST)
        LOGGER.info("Initial file rename completed successfully")
    except Exception as e:
        LOGGER.error(f"Error in initial rename: {e}")

if __name__ == "__main__":
    LOGGER.info("Starting file monitor ...")

    path = os.getenv('MONITOR_DIR')
    api_key = os.getenv('OPENAI_API_KEY')

    if not api_key:
        LOGGER.error("OPENAI_API_KEY environment variable is not set!")
        exit(1)

    if not path:
        LOGGER.error("MONITOR_DIR environment variable is not set!")
        exit(1)

    try:
        renamer = ContextEnhancedRenamer()
        process_initial_rename(path, renamer)
        event_handler = ChangeHandler()
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