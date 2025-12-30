
import os
from dotenv import load_dotenv

load_dotenv(".env.local")
load_dotenv()

print(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")
print(f"PWD: {os.getcwd()}")
