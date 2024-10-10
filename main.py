import uvicorn
from fastapi import FastAPI, Depends, Request, Security
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from dependencies import azure_scheme
from fastapi_azure_auth.user import User
from config import settings
#from ms_dataverse import DataverseORM

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Load OpenID config on startup.
    """
    await azure_scheme.openid_config.load_config()
    yield

app = FastAPI(
    swagger_ui_oauth2_redirect_url='/oauth2-redirect',
    swagger_ui_init_oauth={
        'usePkceWithAuthorizationCodeGrant': True,
        'clientId': settings.OPENAPI_CLIENT_ID,
        'scopes': settings.SCOPE_NAME,
    },
)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

@app.get("/", dependencies=[Security(azure_scheme)])
async def root():
    return {"message": "Hello World"}

@app.get("/list-tables", dependencies=[Security(azure_scheme)])
async def list_tables(request: Request):
    return {"message": request.state}

@app.get("/hello-user",
    response_model=User,
    operation_id='helloWorldApiKey',
    dependencies=[Depends(azure_scheme)]
)
async def hello_user(request: Request) -> dict[str, bool]:
    return request.state.user.dict()

if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)
