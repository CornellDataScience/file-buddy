from watchdog.events import FileSystemEventHandler
from file_parsers.image import describe_image
import logging
from pinecone import Pinecone
from openai import OpenAI
import uuid
import os
LOGGER = logging.getLogger(__name__)

USER_ID = os.getenv('USER_ID')

def get_chunks(path):
    match path:
        case path if path.endswith(('.png', '.jpg', '.jpeg')):
            return describe_image(path)
        case _: # add text processing, pdf processing, etc. here
            return []

class ChangeHandler(FileSystemEventHandler):
    def on_created(self, event):
        LOGGER.info(f'File {event.src_path} has been created')
        chunks = get_chunks(event.src_path)
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
        index = pc.Index(os.getenv('PINECONE_INDEX_NAME'))
        metadata = {
            'user_id': USER_ID,
            'path': event.src_path,
            'filename': os.path.basename(event.src_path),
            'file_type': os.path.splitext(event.src_path)[1],
            'size_bytes': os.path.getsize(event.src_path),
            'created_time': os.path.getctime(event.src_path),
        }
        for chunk in chunks:
            embedding = client.embeddings.create(input=chunk, model="text-embedding-3-small").data[0].embedding
            index.upsert(vectors=[{
                'id': str(uuid.uuid4()),
                'values': embedding,
                'metadata': metadata
            }])
        LOGGER.info(f'Upserted {len(chunks)} chunks to Pinecone for file {event.src_path}')


    def on_modified(self, event):
        LOGGER.info(f'File {event.src_path} has been modified')

    def on_deleted(self, event):
        LOGGER.info(f'File {event.src_path} has been deleted')