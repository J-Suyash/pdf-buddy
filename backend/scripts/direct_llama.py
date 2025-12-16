from llama_cloud_services import LlamaExtract
from pydantic import BaseModel, Field

# bring in our LLAMA_CLOUD_API_KEY
from dotenv import load_dotenv
load_dotenv()

# Initialize client
extractor = LlamaExtract()

# Define schema using Pydantic
agents = extractor.list_agents()
print(agents)
