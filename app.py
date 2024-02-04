from datetime import datetime, timezone
import os
import psycopg2
from dotenv import load_dotenv
from flask import Flask, request

CREATE_ROOMS_TABLE = (
        "CREATE TABLE IF NOT EXISTS rooms (id serial primary key, name text);"
)

CREATE_TEMPS_TABLE = """create table if not exists temperatures (
    room_id integer, 
    temperature Real, 
    date timestamp, 
    foreign key(room_id) references rooms(id) on delete cascade
);"""
INSERT_ROOM_RETURN_ID ="Insert into rooms(name) values (%s) returning id;"
INSERT_TEMP=(
        "insert into temperatures (room_id, temperature, date) values(%s,%s,%s);"
)
GLOBAL_NUMBER_OF_DAYS=(
        """SELECT COUNT(DISTINCT DATE(date)) AS days FROM temperatures;"""
)

GLOBAL_AVG= """SELECT AVG(temperature) as average FROM temperature;"""

load_dotenv()

app = Flask(__name__)
url = os.getenv("DATABASE_URL")
connection = psycopg2.connect(url)

@app.post("/api/room")
def create_room():
    data = request.get_json()
    name = data["name"]
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_ROOMS_TABLE)
            cursor.execute(INSERT_ROOM_RETURN_ID,(name,))
            room_id = cursor.fetchone()[0]
    return {"id":room_id,"message": f"Room {name} created."}, 

@app.post("/api/temperature")
def add_temp():
    data = request.get_json()
    temperature = data["temperature"]
    room_id=data["room"]
    try:
        date = datetime.strptime(data["date"], "%m-%d-%Y %H:%M:%S")
    except KeyError:
        date = datetime.now(timezone.utc)
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_TEMPS_TABLE)
            cursor.execute(INSERT_TEMP, (room_id,temperature, date))
    return{"message": "temperature added " }, 201

@app.get("/api/average")
def get_global_avg():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(GLOBAL_AVG)
            average=cursor.fetchone()[0]
            cursor.execute(GLOBAL_NUMBER_OF_DAYS)
            days=cursor.fetchone()[0]
    return {"average": round(average,2),"days": days}        
