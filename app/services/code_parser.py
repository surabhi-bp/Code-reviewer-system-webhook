"""
Filename: app/services/code_parser.py
Description: Service for parsing unified git diff content into file-by-file patches.
"""

import re
from typing import List, Dict

class CodeParserService:
    """Service to parse raw git diffs and extract file patches."""

    def parse_diff(self, raw_diff: str) -> List[Dict[str, str]]:
        """
        Parse a unified git diff into a list of file paths and patch details.
        
        Args:
            raw_diff: Raw unified diff content as a string.
            
        Returns:
            List[Dict[str, str]]: A list of dictionaries containing 'file_path' and 'patch' keys.
        """
        if not raw_diff:
            return []
            
        parsed_files: List[Dict[str, str]] = []
        current_file: str = ""
        current_patch_lines: List[str] = []
        
        # Split raw_diff into lines
        lines = raw_diff.splitlines()
        
        for line in lines:
            # Detect file headers
            if line.startswith("+++ b/"):
                # If there's an ongoing file, save it
                if current_file and current_patch_lines:
                    parsed_files.append({
                        "file_path": current_file,
                        "patch": "\n".join(current_patch_lines)
                    })
                current_file = line[6:]
                current_patch_lines = []
            elif line.startswith("+++ "):
                # Fallback check for paths that may not start with b/
                if current_file and current_patch_lines:
                    parsed_files.append({
                        "file_path": current_file,
                        "patch": "\n".join(current_patch_lines)
                    })
                current_file = line[4:]
                current_patch_lines = []
            elif line.startswith("--- ") or line.startswith("diff ") or line.startswith("index "):
                # Skip diff header metadata lines
                continue
            else:
                # If we've started tracking a file, accumulate lines
                if current_file:
                    current_patch_lines.append(line)
                    
        # Append final file if it exists
        if current_file and current_patch_lines:
            parsed_files.append({
                "file_path": current_file,
                "patch": "\n".join(current_patch_lines)
            })
            
        return parsed_files
