import os
from pathlib import Path
import json
from file_renamer import FileRenameHandler
from Folder_Context import get_file_content, summarize_content, build_directory_tree

class ContextEnhancedRenamer:
    def __init__(self):
        self.renamer = FileRenameHandler()
    
    def get_file_context(self, directory: str) -> dict:
        """Get context information for all files in directory"""
        print(f"Analyzing directory: {directory}")
        files_context = {}
        directory_path = Path(directory)
        
        # Get directory tree for overall context
        tree = build_directory_tree(directory_path)
        
        for file in os.listdir(directory):
            print(f"Processing file: {file}")
            file_path = Path(os.path.join(directory, file))
            if file_path.is_file():
                # Get content and summary
                content = get_file_content(file_path)
                summary = summarize_content(content) if content else "No summary available"
                
                # Get contextual information
                files_context[file] = {
                    "summary": summary,
                    "directory": file_path.parent.name,
                    "siblings": [f.name for f in file_path.parent.iterdir() 
                               if f.is_file() and f != file_path]
                }
        
        return files_context
    
    def enhance_naming_request(self, original_request: str, context: dict) -> str:
        """Enhance the naming request with context information"""
        return f"""Consider this context about the files:
        {json.dumps(context, indent=2)}
        
        Original naming request: {original_request}
        
        Use the file contents and relationships to generate appropriate names 
        that reflect both the request and the context of the files.
        """
    
    def process_context_aware_rename(self, directory: str, naming_request: str) -> dict:
        """Process rename request with enhanced context"""
        # Get context for all files
        context = self.get_file_context(directory)
        
        # Enhance the naming request with context
        enhanced_request = self.enhance_naming_request(naming_request, context)
        
        # Process the enhanced request
        return self.renamer.process_rename_request(directory, enhanced_request)