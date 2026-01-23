import vertexai
import os
from dotenv import load_dotenv

# 在所有其他匯入之前，從 .env 檔案載入環境變數
load_dotenv()

GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "asia-east1")

client = vertexai.Client(
    project=GOOGLE_CLOUD_PROJECT,
    location=GOOGLE_CLOUD_LOCATION,
)

agent_engine = client.agent_engines.create()

# Optionally, print out the Agent Engine resource name. You will need the
# resource name to interact with your Agent Engine instance later on.
print(agent_engine.api_resource.name)
print("Agent Engine created successfully.")
print("Agent Engine ID:", agent_engine.api_resource.name.split("/")[-1])
print("You can now use this Agent Engine in your applications.")

# ref: 
#   - https://docs.cloud.google.com/agent-builder/agent-engine/memory-bank/set-up?hl=zh-tw
#   - https://google.github.io/adk-docs/sessions/memory/#configuration
