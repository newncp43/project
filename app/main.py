import uvicorn
from fastapi import FastAPI, Path, Query, HTTPException
from starlette.responses import JSONResponse
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware

from database.mongodb import MongoDB
from config.development import config
from model.student import createStudentModel, updateStudentModel

mongo_config = config["mongo_config"]
mongo_db = MongoDB(
    mongo_config["host"],
    mongo_config["port"],
    mongo_config["user"],
    mongo_config["password"],
    mongo_config["auth_db"],
    mongo_config["db"],
    mongo_config["collection"],
)
mongo_db._connect()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def index():
    return JSONResponse(content={"message": "Student Info"}, status_code=200)


@app.get("/user")
def get_user(
    sort_by: Optional[str] = None,
    order: Optional[str] = Query(None, min_length=3, max_length=4),
):

    try:
        result = mongo_db.find(sort_by, order)
    except:
        raise HTTPException(status_code=500, detail="Something went wrong !!")

    return JSONResponse(
        content={"status": "OK", "data": result},
        status_code=200,
    )


@app.get("/user/{user_id}")
def get_user_by_id(user_id: str = Path(None, min_length=10, max_length=10)):
    try:
        result = mongo_db.find_one(user_id)
    except:
        raise HTTPException(status_code=500, detail="Something went wrong !!")

    if result is None:
        raise HTTPException(status_code=404, detail="Student Id not found !!")

    return JSONResponse(
        content={"status": "OK", "data": result},
        status_code=200,
    )


@app.post("/user")
def create_books(user: createStudentModel):
    try:
        user_id = mongo_db.create(user)
    except:
        raise HTTPException(status_code=500, detail="Something went wrong !!")

    return JSONResponse(
        content={
            "status": "ok",
            "data": {
                "student_id": user_id,
            },
        },
        status_code=201,
    )


@app.patch("/user/{user_id}")
def update_books(
    user: updateStudentModel,
    user_id: str = Path(None, min_length=10, max_length=10),
):
    print("user", user)
    try:
        updated_user_id, modified_count = mongo_db.update(user_id, user)
    except:
        raise HTTPException(status_code=500, detail="Something went wrong !!")

    if modified_count == 0:
        raise HTTPException(
            status_code=404,
            detail=f"user Id: {updated_user_id} is not update want fields",
        )

    return JSONResponse(
        content={
            "status": "ok",
            "data": {
                "student_id": updated_user_id,
                "modified_count": modified_count,
            },
        },
        status_code=200,
    )


@app.delete("/user/{user_id}")
def delete_book_by_id(user_id: str = Path(None, min_length=10, max_length=10)):
    try:
        deleted_user_id, deleted_count = mongo_db.delete(user_id)
    except:
        raise HTTPException(status_code=500, detail="Something went wrong !!")

    if deleted_count == 0:
        raise HTTPException(
            status_code=404, detail=f"user Id: {deleted_user_id} is not Delete"
        )

    return JSONResponse(
        content={
            "status": "ok",
            "data": {
                "student_id": deleted_user_id,
                "deleted_count": deleted_count,
            },
        },
        status_code=200,
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=3001, reload=True)
