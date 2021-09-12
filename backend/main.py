import logging
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Dict, List

from dotenv import load_dotenv
from fastapi import FastAPI, Response, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from external.google_datastore.datastore import get_all_user_ids

load_dotenv()

# flake8: noqa E402

# add endpoints here (after load dotenv)
from constants import PUBSUB_PUB

from endpoints.user import main as _get_user
from endpoints.github_auth import get_access_token

"""
SETUP
"""

app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

"""
HELPER FUNCTIONS
"""


@app.get("/")
async def read_root():
    return {"Hello": "World"}


def fail_gracefully(func: Callable[..., Any]):
    @wraps(func)  # needed to play nice with FastAPI decorator
    def wrapper(response: Response, *args: List[Any], **kwargs: Dict[str, Any]) -> Any:
        start = datetime.now()
        try:
            data = func(response, *args, **kwargs)
            return {"data": data, "message": "200 OK", "time": datetime.now() - start}
        except Exception as e:
            logging.exception(e)
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {
                "data": [],
                "message": "Error " + str(e),
                "time": datetime.now() - start,
            }

    return wrapper


def async_fail_gracefully(func: Callable[..., Any]):
    @wraps(func)  # needed to play nice with FastAPI decorator
    async def wrapper(
        response: Response, *args: List[Any], **kwargs: Dict[str, Any]
    ) -> Any:
        start = datetime.now()
        try:
            data = await func(response, *args, **kwargs)
            return {"data": data, "message": "200 OK", "time": datetime.now() - start}
        except Exception as e:
            logging.exception(e)
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {
                "data": [],
                "message": "Error " + str(e),
                "time": datetime.now() - start,
            }

    return wrapper


"""
USER LOGIN
"""


@app.post("/login/{code}", status_code=status.HTTP_200_OK)
@fail_gracefully
def login(response: Response, code: str) -> Any:
    if not PUBSUB_PUB:
        raise HTTPException(500, "Login using PUB Server, not SUB Server")
    return get_access_token(code)


"""
ENDPOINTS
"""


@app.get("/user/{user_id}", status_code=status.HTTP_200_OK)
@async_fail_gracefully
async def get_user(response: Response, user_id: str) -> Any:
    return await _get_user(user_id)


@app.get("/user_refresh", status_code=status.HTTP_200_OK)
@async_fail_gracefully
async def get_user_refresh(response: Response) -> Any:
    data = get_all_user_ids()
    for user_id in data:
        try:
            await _get_user(user_id, use_cache=False)
        except Exception as e:
            print(e)
    return "Successfully Updated"
