from fastapi import APIRouter, Response
import os
from .single_ssl import create_certificate
# from fastapi.responses import JSONResponse


ssl_router = APIRouter()


@ssl_router.get("/single_ssl/{domain}/create")
async def create(domain: str):
    try:
        return await create_certificate(domain)
    except Exception as e:
        print(e)


@ssl_router.get("/.well-known/acme-challenge/{challenge_route}")
async def get_certificate(challenge_route: str):
    try:
        if challenge_route == 'test':
            return {"message": "success"}
        full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'cname_ssl_v7', 'module', 'ssl', 'temp_ssl', 'test.hqsmaxtest.online')
        with open(os.path.join(full_path, '.well-known', 'acme-challenge', challenge_route), 'r') as f:
            content = f.read()
        return Response(content)
    except Exception as e:
        print(e)

