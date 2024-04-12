from dotenv import load_dotenv
import os
 
load_dotenv()
 

config = {
    "TOKEN": os.getenv("TOKEN"),
    "GITHUB_API_URL": os.getenv("GITHUB_API_URL"),
    "ORG": os.getenv("ORG"),
    "ELASTIC_SEARCH_URL": os.getenv("ELASTIC_SEARCH_URL")
}

