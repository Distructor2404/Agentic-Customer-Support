import os
import logging
import uvicorn

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import endpoints as CustomerSupport

load_dotenv()

if len(logging.getLogger().handlers) > 0:
    logging.getLogger().setLevel(logging.INFO)
else:
    logging.basicConfig(level=logging.INFO)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


app.include_router(
    CustomerSupport.router,
    prefix="/customer-support",
    tags=["Customer Support APIs"]
)


@app.get("/health-check/", status_code=status.HTTP_200_OK)
def health_check(request: Request):
    return JSONResponse(content={"status": "Healthy"})
