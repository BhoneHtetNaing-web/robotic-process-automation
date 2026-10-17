from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router

from app.core.config import get_settings

settings = get_settings()

app = FastAPI(

    title=settings.APP_NAME,

    version="0.1.0",

    description=(

        "Secure integration foundation for authorized MPT "

        "network telemetry and automation."

    ),

    docs_url="/docs" if settings.APP_ENV != "production" else None,

    redoc_url=None,

)

# Keep browser origins explicit when the frontend is introduced.

# Do not use wildcard origins together with credentialed requests.

app.add_middleware(

    CORSMiddleware,

    allow_origins=[],

    allow_credentials=False,

    allow_methods=["GET", "POST"],

    allow_headers=[

        "Authorization",

        "Content-Type",

        "X-Apexive-Timestamp",

        "X-Apexive-Signature",

    ],

)

app.include_router(

    router,

    prefix=settings.API_PREFIX,

)

@app.get("/")

def root():

    return {

        "service": settings.APP_NAME,

        "status": "running",

        "network_data": "NOT_CONNECTED",

    }