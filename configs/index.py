import os
from dotenv import load_dotenv
from prisma import Prisma


load_dotenv()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
REDIS_URL = os.getenv("REDIS_URL")
db = Prisma()
