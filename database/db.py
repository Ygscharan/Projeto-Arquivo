from urllib.parse import quote
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

USER = os.getenv("USER")
PASSWD = os.getenv('PASSWORD')
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
SID = os.getenv("SID")

instance = f"oracle+oracledb://{USER}:{PASSWD}@{HOST}/?service_name={SID}"
engine = create_engine(instance, echo=False,)

session = scoped_session(sessionmaker(bind=engine))


print(instance)
