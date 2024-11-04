from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import urllib.parse
import os

load_dotenv()

username = "atla_smokinghot"
password = urllib.parse.quote_plus("cj6Jr037yzt9l7K5")  # Your password here
hostname = "atlaswavestrader.com"
database_name = "atla_traderapp"


SQLALCHEMY_DATABASE_URL = "sqlite:///./finno_trader.db"
URL_DATABASE = f"mysql+pymysql://{username}:{password}@{hostname}/{database_name}"
# SQLALCHEMY_DATABASE_URL = os.getenv("SQL_URL")
# URL_DATABASE = f"mysql+pymysql://trader_app_user:ChiefDaddy123!!@93.127.203.25:3306/traderapp"

engine = create_engine(
    # URL_DATABASE
    SQLALCHEMY_DATABASE_URL
    # connect_args={"check_same_thread": False}

)
# connect_args={"check_same_thread": False} should be removed on live

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()

