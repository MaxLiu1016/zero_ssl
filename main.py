from fastapi import FastAPI
from module.ssl.router import ssl_router
from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional
from typing import Annotated
# import models as dbmdls
# from database import engine, SessionLocal
# from sqlalchemy.orm import Session
from datetime import datetime
import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.dnspod.v20210323 import dnspod_client, models

app = FastAPI()
# dbmdls.Base.metadata.create_all(bind=engine)
cred = credential.Credential("IKIDd6Ukrz59LfyKZouoeJtPq44sVxDG7qKc", "ACPSOEyb5NWTApQq8MoDWffhbKq8D5mK")
httpProfile = HttpProfile()
httpProfile.endpoint = "dnspod.tencentcloudapi.com"
clientProfile = ClientProfile()
clientProfile.httpProfile = httpProfile
client = dnspod_client.DnspodClient(cred, "", clientProfile)

class RecordCreate(BaseModel):
    Domain: str
    DomainId: Optional[int] = None
    SubDomain: Optional[str] = None
    RecordType: str
    RecordLine: Optional[str] = "默认"
    RecordLineId: Optional[str] = None
    Value: str
    MX: Optional[int] = None
    TTL: Optional[int] = None
    Weight: Optional[int] = None
    Status: Optional[str] = None
    RecordId: Optional[int] = None


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/domains/{domain_name}", status_code=status.HTTP_201_CREATED)
async def create_domain(domain_name:str):
    req = models.CreateDomainRequest()
    params = {
        "Domain": domain_name
    }
    req.from_json_string(json.dumps(params))
    resp = client.CreateDomain(req)
    domain_result = json.loads(resp.to_json_string())
    domain_domain_info = domain_result['DomainInfo']
    domain_domain_info['GradeNsList'] = str(domain_domain_info.get('GradeNsList'))
    # m = dbmdls.Domain(**domain_domain_info)
    # db.add(m)
    # db.commit()
    return resp.to_json_string()


app.include_router(ssl_router)