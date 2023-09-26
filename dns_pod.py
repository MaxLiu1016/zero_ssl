from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional
from typing import Annotated
import models as dbmdls
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from datetime import datetime
import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.dnspod.v20210323 import dnspod_client, models

app = FastAPI()
dbmdls.Base.metadata.create_all(bind=engine)
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

class RecordDelete(BaseModel):
    Domain: str
    DomainId: Optional[int] = None
    RecordId: int

class RecordUpdte(BaseModel):
    Domain: str
    RecordType: str
    RecordLine: str
    Value: str
    RecordId: int
    DomainId: Optional[int] = None
    SubDomain: Optional[str] = None
    RecordLineId: Optional[str] = None
    MX: Optional[int] = None
    TTL: Optional[int] = None
    Weight: Optional[int] = None
    Status: Optional[str] = None
    
class RecordRead(BaseModel):
    Domain: str
    RecordId: int


class DomainListBase(BaseModel):
    DomainId: str
    Name: str
    Status: int
    TTL: int
    CNAMESpeedup: str
    DNSStatus: str
    Grade: str
    GroupId: int
    SearchEnginePush: str
    Remark: str
    Punycode: str
    EffectiveDNS: str
    GradeLevel: int
    GradeTitle: str
    IsVip: str
    VipStartAt: datetime
    VipEndAt: datetime
    VipAutoRenew: str
    RecordCount: int
    CreatedOn: datetime
    UpdatedOn: datetime
    Owner: str
    TagList: str


class DomianBase(BaseModel):
    Domain: str
    Punycode: str
    GradeNsList: str
    

class PostBase(BaseModel):
    title: str
    content: str
    user_id: int


class UserBase(BaseModel):
    username: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

# 新增 NS 外層
@app.post("/domains/{domain_name}", status_code=status.HTTP_201_CREATED)
async def create_domain(domain_name:str, db: db_dependency):
    req = models.CreateDomainRequest()
    params = {
        "Domain": domain_name
    }
    req.from_json_string(json.dumps(params))
    resp = client.CreateDomain(req)
    domain_result = json.loads(resp.to_json_string())
    domain_domain_info = domain_result['DomainInfo']
    domain_domain_info['GradeNsList'] = str(domain_domain_info.get('GradeNsList'))
    m = dbmdls.Domain(**domain_domain_info)
    db.add(m)
    db.commit()
    return resp.to_json_string()

#刪除 NS 外層
@app.delete("/domains/{domain_name}", status_code=status.HTTP_200_OK)
async def delete_domain(domain_name:str, db: db_dependency):
    req = models.DeleteDomainRequest()
    params = {
        "Domain": domain_name
    }
    req.from_json_string(json.dumps(params))
    resp = client.DeleteDomain(req)
    
    db_domain = db.query(dbmdls.Domain).filter(dbmdls.Domain.Domain == domain_name).first()
    if db_domain is None:
        raise HTTPException(status_code=404, detail='Domain not found')
    db.delete(db_domain)
    db.commit()
    return resp.to_json_string()

# 新增 NS 內記錄(含TXT、CANME記錄)
@app.post("/domains/", status_code=status.HTTP_201_CREATED)
async def create_record(RecordCreate: RecordCreate, db: db_dependency):
    #新增recored 後返回 RecordID，然後再打一次Record細節，再返回後取得完整的Record訊息後寫入
    #又或者返回後id 直接create 到DB

    req = models.CreateRecordRequest()
    params = RecordCreate.dict()
    req.from_json_string(json.dumps(params))
    resp = client.CreateRecord(req)
    recored_create_result = json.loads(resp.to_json_string())
    print(recored_create_result['RecordId'])
    # m = dbmdls.Record(**recored_create_result)
    # db.add(m)
    # db.commit()
    return recored_create_result['RecordId']

    

# 刪除 NS 內記錄(含TXT、CANME記錄)
@app.delete("/domains/", status_code=status.HTTP_201_CREATED)
async def delete_record(RecordDelete: RecordDelete, db: db_dependency):
    #先查詢DB有沒有Domain，有的話再打DnsPod 新增 Record，防呆機制
    req = models.DeleteRecordRequest()
    params = RecordDelete.dict()
    req.from_json_string(json.dumps(params))
    resp = client.DeleteRecord(req)
    return resp.to_json_string()    

# 取得單一域名record
@app.post("/record/", status_code=status.HTTP_201_CREATED)
async def read_record(RecordRead: RecordRead, db: db_dependency):
    req = models.DescribeRecordRequest()
    params = RecordRead.dict()
    req.from_json_string(json.dumps(params))
    resp = client.DescribeRecord(req)
    record_read_result = json.loads(resp.to_json_string())
    # m = dbmdls.Record(**dnspod_create_result)
    # db.add(m)
    # db.commit()
    return record_read_result

#列出清單
@app.post("/get_domains_list/", status_code=status.HTTP_201_CREATED)
async def create_domain_list(db: db_dependency):
    try:
        req = models.DescribeDomainListRequest()
        params = {

        }
        req.from_json_string(json.dumps(params))
        resp = client.DescribeDomainList(req)
        domain_list = json.loads(resp.to_json_string())
        all_domain_data = domain_list['DomainList']
        for domain_data in all_domain_data:
            domain_data['EffectiveDNS'] = str(domain_data.get('EffectiveDNS'))
            m = dbmdls.DomainList(**domain_data)
            db.add(m)
            db.commit()
        return resp.to_json_string()
    except TencentCloudSDKException as err:
        return err


# 修改指向(高防/黑洞用)
@app.put("/domains/", status_code=status.HTTP_201_CREATED)
async def update_record(RecordUpdte: RecordUpdte, db: db_dependency):
    req = models.ModifyRecordRequest()
    params = RecordUpdte.dict()
    req.from_json_string(json.dumps(params))
    resp = client.ModifyRecord(req)
    print(resp.to_json_string())
    return resp.to_json_string()


# 從DB 取出單一域名
@app.get("/domains/{domain_id}", status_code=status.HTTP_200_OK)
async def read_domain(domain_id: int, db: db_dependency):
    domain = db.query(dbmdls.Domain).filter(dbmdls.Domain.Id == domain_id).first()
    if domain is None:
        raise HTTPException(status_code=404, detail='Domain not found')
    return domain





# @app.get("/posts/{post_id}", status_code=status.HTTP_200_OK)
# async def read_post(post_id: int, db: db_dependency):
#     post = db.query(models.Post).filter(models.Post.id == post_id).first()
#     if post is None:
#         raise HTTPException(status_code=404, detail='Post not found')
#     return post


# @app.delete("/posts/{post_id}", status_code=status.HTTP_200_OK)
# async def delete_post(post_id:int, db: db_dependency):
#     db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
#     if db_post is None:
#         raise HTTPException(status_code=404, detail='Post not found')
#     db.delete(db_post)
#     db.commit()

# @app.post("/users/", status_code=status.HTTP_201_CREATED)
# async def create_user(user: UserBase, db: db_dependency):
#     db_user = models.User(**user.dict())
#     db.add(db_user)
#     db.commit()



# @app.get("/users/{user_id}", status_code=status.HTTP_200_OK)
# async def read_user(user_id: int, db: db_dependency):
#     user = db.query(models.User).filter(models.User.id == user_id).first()
#     if user is None:
#         raise HTTPException(status_code=404, detail='User not found')
#     return user