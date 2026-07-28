"""
Filename: app/services/ai/base.py
Description: Abstract Base Class for AI Provider Strategy.
"""

from abc import ABC, abstractmethod

class AIProvider(ABC):
    """Abstract class defining interface for AI completion/generation providers."""

    @abstractmethod
    def analyze(self, prompt: str) -> str:
        """
        Analyze the given prompt and return the model's text response.
        
        Args:
            prompt: Formatted prompt text for the AI.
            
        Returns:
            str: Raw textual output from the model.
        """
        pass
