# main.py

from datetime import date
import os
from fastapi import FastAPI, File, UploadFile
from sqlalchemy import (
    Column,
    Date,
    Engine,
    Integer,
    LargeBinary,
    MetaData,
    String,
    Table,
    select,
    delete,
    create_engine,
    text,
)
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Database connection:
DB_NAME: str = os.getenv("DB_NAME")
DB_USER: str = os.getenv("DB_USER")
DB_PASS: str = os.getenv("DB_PASS")
DB_HOST: str = os.getenv("DB_HOST")
DB_PORT: int = os.getenv("DB_PORT")

conn_string: str = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
db: Engine = create_engine(conn_string)

print(f"Connecting to {conn_string}")

Session = sessionmaker(bind=db)
session = Session()

metadata = MetaData()

table: Table = Table(
    "files",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("file_name", String),
    Column("file_content", LargeBinary),
    Column("created_at", Date),
)

app = FastAPI()


@app.post("/upload")
def upload(file: UploadFile = File(...)):
    try:
        contents = file.file.read()
        with open(file.filename, "rb") as _:
            new_row = table.insert().values(
                file_name=file.filename, file_content=contents, created_at=date.today()
            )
            session.execute(new_row)
            session.commit()
    except Exception as e:
        print(e)
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()

    return {"message": f"Succesfully uploaded {file.filename}"}


@app.get("/retrieve/{filename}")
def retrieve(filename: str):
    try:
        query = select(text("*")).where(table.c.file_name == filename)
        row = session.execute(query).fetchone()
        if row:
            response = {
                "media_type": "application/octet-stream",
                "Content-Disposition": f"attachment; filename={filename}",
                "content": row[2].tobytes(),
            }
            return response
        return {"message": "The requested file name was not found"}
    except Exception:
        return {"message": "Error retrieving file"}


@app.delete("/delete_file/{filename}")
def delete_file(filename: str):
    try:
        query = delete(table).where(table.c.file_name == filename)
        session.execute(query)
        session.commit()
        return {"message": "Operation complete"}
    except Exception:
        return {"message": "A problem was encountered on deleting"}
