import os
from dotenv import load_dotenv
from prisma import Prisma


load_dotenv()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
REDIS_URL = os.getenv("REDIS_URL")
db = Prisma()
db.connect()
PINECONE_API_KEY= os.getenv("PINECONE_API_KEY")
PINECONE_HOST_URL= os.getenv("PINECONE_HOST_URL")