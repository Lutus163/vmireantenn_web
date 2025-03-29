import requests
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

def ngrok_script_output():
    NGROK_AUTH_TOKEN = "2f1J9UYsgn0lwY8XD2cAS4FLYfq_7hUAaB4csbQ6YLWYxZ6UA"
    ngrok_url = ''

    try:
        response = requests.get("http://localhost:4040/api/tunnels")

        if response.status_code == 200:
            ngrok_url = response.json()['tunnels'][0]['public_url']

            engine = create_engine("sqlite:///links.sqlite3")
            Base = declarative_base()

            class Link(Base):
                __tablename__ = 'links'
                id = Column(Integer, primary_key=True)
                url = Column(String)

            Base.metadata.create_all(engine)

            Session = sessionmaker(bind=engine)
            session = Session()

            new_link = Link(url=ngrok_url)
            session.add(new_link)
            session.commit()
        else:
            print("Failed to retrieve ngrok URL. Status code:", response.status_code)

    except Exception as e:
        print("An error occurred:", e)

    return ngrok_url