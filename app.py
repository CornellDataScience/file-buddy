import os
from watchdog.observers.polling import PollingObserver as Observer
import time
import logging
from file_handler import ChangeHandler

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    LOGGER.info("Starting file monitor ...")

    path = os.getenv('MONITOR_DIR')
    event_handler = ChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        LOGGER.info("Shutting down...")
        observer.stop()
    observer.join()
