from fastapi import APIRouter, Response
import os

from .san_ssl import create_san_certificate
from .single_ssl import create_certificate
from .wild_card import create_wild_card
# from fastapi.responses import JSONResponse


ssl_router = APIRouter()


@ssl_router.get("/single_ssl/{domain}/create")
async def create(domain: str):
    try:
        return await create_certificate(domain)
    except Exception as e:
        print(e)


@ssl_router.get("/wild_card/{domain}/create")
async def create_wild(domain: str):
    try:
        return await create_wild_card(domain)
    except Exception as e:
        print(e)


@ssl_router.get("/san_card/{domains}/create")
async def create_san(domains: str):
    domains = domains.split(',')
    try:
        return await create_san_certificate(domains)
    except Exception as e:
        print(e)


@ssl_router.get("/.well-known/acme-challenge/{challenge_route}")
async def get_certificate(challenge_route: str):
    try:
        if challenge_route == 'acme-pre-test':
            return {"message": "This is for acme pre-test"}
        full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                 'ssl', 'temp', 'challenge_file')
        with open(os.path.join(full_path, '.well-known', 'acme-challenge', challenge_route), 'r') as f:
            content = f.read()
        return Response(content)
    except Exception as e:
        print(e)

