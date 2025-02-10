import logging
from langchain_core.callbacks import BaseCallbackHandler

class TokenUsageHandler(BaseCallbackHandler):
    def __init__(self):
        self.input_tokens = 0
        self.output_tokens = 0
        self.total_tokens = 0

    def on_llm_end(self, response, **kwargs):
       # Assuming 'result' is the object you received
        usage_metadata = response.generations[0][0].message.response_metadata['token_usage']

        if usage_metadata:
            self.input_tokens = usage_metadata['prompt_tokens']
            self.output_tokens = usage_metadata['completion_tokens']
            self.total_tokens = usage_metadata['total_tokens']
            
    def log_token_usage(self, logger: logging.Logger):
        logger.info(f"Input Tokens: {self.input_tokens}")
        logger.info(f"Output Tokens: {self.output_tokens}")
        logger.info(f"Total Tokens: {self.total_tokens}")