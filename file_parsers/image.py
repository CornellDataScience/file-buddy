import base64
import os
import logging
from openai import OpenAI

LOGGER = logging.getLogger(__name__)

def describe_image(image_path):
    """
    Uses GPT-4 Vision to generate a text description of an image.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        list[str]: List of text descriptions of the image, or None if there was an error
    """
    try:
        client = OpenAI()
        
        # Read image file
        with open(image_path, "rb") as image_file:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that can describe images in detail. Your descriptions are used to index images in a vector database. Describe the image in detail, including the context of the image, the objects, the colors, the lighting, the composition, and any other relevant details. Limit your response to a single paragraph."
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text", 
                                "text": "Please describe this image."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64.b64encode(image_file.read()).decode()}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=300
            )
            
        return [response.choices[0].message.content]
        
    except Exception as e:
        LOGGER.error(f"Error describing image {image_path}: {str(e)}")
        return None

