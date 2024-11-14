# file_renamer.py

import os
import re
from typing import List, Tuple, Dict
import logging
from openai import OpenAI
from openai.types.chat import ChatCompletion

LOGGER = logging.getLogger(__name__)

class FileRenameHandler:
    def __init__(self):  # Remove api_key parameter
        """Initialize the FileRenameHandler.
        The OpenAI client will automatically use the OPENAI_API_KEY environment variable."""
        try:
            self.client = OpenAI()  # No need to pass api_key explicitly
            LOGGER.info("OpenAI client initialized successfully")
        except Exception as e:
            LOGGER.error(f"Failed to initialize OpenAI client: {e}")
            raise
        
    def _generate_rename_prompt(self, files: List[str], naming_request: str) -> str:
        """Generate a prompt for GPT-4 to create regex and new filenames."""
        return f"""Given these files: {', '.join(files)}
        And this naming convention request: "{naming_request}"
        
        Please provide:
        1. A Python regex pattern that matches the desired naming convention
        2. A list of new filenames for each file that follow the convention
        
        Format your response exactly like this:
        REGEX: ^your_regex_pattern$
        NAMES:
        original_name1.ext -> new_name1.ext
        original_name2.ext -> new_name2.ext
        
        Ensure the regex is strict and the new names maintain original extensions.
        """
        
    def _parse_gpt_response(self, response: str) -> Tuple[str, Dict[str, str]]:
        """Parse GPT's response to extract regex and filename mappings."""
        try:
            # Split into regex and names sections
            regex_part, names_part = response.strip().split('NAMES:', 1)
            regex_pattern = regex_part.replace('REGEX:', '').strip()
            
            # Parse filename mappings
            name_mappings = {}
            for line in names_part.strip().split('\n'):
                if '->' in line:
                    old_name, new_name = line.split('->')
                    name_mappings[old_name.strip()] = new_name.strip()
                    
            return regex_pattern, name_mappings
        except Exception as e:
            LOGGER.error(f"Failed to parse GPT response: {e}")
            raise ValueError("Invalid GPT response format")
            
    def _validate_new_names(self, regex_pattern: str, new_names: List[str]) -> bool:
        """Validate that new names match the regex pattern."""
        try:
            pattern = re.compile(regex_pattern)
            return all(pattern.match(name) for name in new_names)
        except re.error as e:
            LOGGER.error(f"Invalid regex pattern: {e}")
            return False
            
    def process_rename_request(self, directory: str, naming_request: str) -> Dict[str, str]:
        """Process the rename request and return mapping of old to new names."""
        # Get list of files in directory
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        
        if not files:
            LOGGER.warning(f"No files found in directory: {directory}")
            return {}
            
        # Generate GPT prompt and get response
        prompt = self._generate_rename_prompt(files, naming_request)
        
        try:
            response: ChatCompletion = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates regex patterns and filenames based on naming conventions."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Parse GPT response
            regex_pattern, name_mappings = self._parse_gpt_response(response.choices[0].message.content)
            
            # Validate new names against regex
            new_names = list(name_mappings.values())
            if not self._validate_new_names(regex_pattern, new_names):
                raise ValueError("Generated names don't match the regex pattern")
                
            return name_mappings
            
        except Exception as e:
            LOGGER.error(f"Error in rename request processing: {e}")
            raise
            
    def apply_rename(self, directory: str, name_mappings: Dict[str, str]) -> None:
        """Apply the rename operations to files in the directory."""
        for old_name, new_name in name_mappings.items():
            old_path = os.path.join(directory, old_name)
            new_path = os.path.join(directory, new_name)
            
            try:
                if os.path.exists(old_path):
                    os.rename(old_path, new_path)
                    LOGGER.info(f"Renamed '{old_name}' to '{new_name}'")
                else:
                    LOGGER.warning(f"File not found: {old_name}")
            except OSError as e:
                LOGGER.error(f"Error renaming {old_name}: {e}")