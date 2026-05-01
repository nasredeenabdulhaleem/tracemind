"""Base agent class for watsonx.ai integration"""

from typing import Dict, Any, Optional
import logging
from ibm_watsonx_ai.foundation_models import Model
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

from app.config import settings

logger = logging.getLogger(__name__)


class BaseAgent:
    """Base class for all AI agents using watsonx.ai"""
    
    # Default model parameters
    DEFAULT_PARAMS = {
        GenParams.MAX_NEW_TOKENS: 1024,
        GenParams.TEMPERATURE: 0.7,
        GenParams.TOP_P: 0.9,
        GenParams.TOP_K: 50
    }
    
    def __init__(
        self,
        model_id: str = "ibm/granite-13b-chat-v2",
        params: Optional[Dict] = None
    ):
        """
        Initialize base agent
        
        Args:
            model_id: watsonx.ai model ID
            params: Generation parameters (optional)
        """
        self.model_id = model_id
        self.params = params or self.DEFAULT_PARAMS.copy()
        self.model = None
        self._init_model()
    
    def _init_model(self):
        """Initialize watsonx.ai model"""
        try:
            credentials = {
                "url": settings.watsonx_url,
                "apikey": settings.watsonx_api_key
            }
            
            self.model = Model(
                model_id=self.model_id,
                params=self.params,
                credentials=credentials,
                project_id=settings.watsonx_project_id
            )
            
            logger.info(f"Initialized watsonx.ai model: {self.model_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize watsonx.ai model: {e}")
            raise
    
    def generate(self, prompt: str) -> str:
        """
        Generate text using watsonx.ai
        
        Args:
            prompt: Input prompt
            
        Returns:
            Generated text
        """
        try:
            response = self.model.generate_text(prompt=prompt)
            return response.strip()
            
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise
    
    def generate_with_retry(
        self,
        prompt: str,
        max_retries: int = 3
    ) -> Optional[str]:
        """
        Generate text with retry logic
        
        Args:
            prompt: Input prompt
            max_retries: Maximum number of retries
            
        Returns:
            Generated text or None if all retries fail
        """
        for attempt in range(max_retries):
            try:
                return self.generate(prompt)
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    logger.error(f"All {max_retries} attempts failed")
                    return None
        
        return None
    
    def build_prompt(self, **kwargs) -> str:
        """
        Build prompt for the agent (to be overridden by subclasses)
        
        Args:
            **kwargs: Prompt parameters
            
        Returns:
            Formatted prompt string
        """
        raise NotImplementedError("Subclasses must implement build_prompt()")
    
    def process(self, **kwargs) -> Dict[str, Any]:
        """
        Process input and return result (to be overridden by subclasses)
        
        Args:
            **kwargs: Processing parameters
            
        Returns:
            Processing result dictionary
        """
        raise NotImplementedError("Subclasses must implement process()")

# Made with Bob