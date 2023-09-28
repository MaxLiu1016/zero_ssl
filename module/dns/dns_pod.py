import json
from pydantic import BaseModel
from typing import Optional
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.dnspod.v20210323 import dnspod_client, models


cred = credential.Credential("IKIDd6Ukrz59LfyKZouoeJtPq44sVxDG7qKc", "ACPSOEyb5NWTApQq8MoDWffhbKq8D5mK")
httpProfile = HttpProfile()
httpProfile.endpoint = "dnspod.tencentcloudapi.com"
clientProfile = ClientProfile()
clientProfile.httpProfile = httpProfile
client = dnspod_client.DnspodClient(cred, "", clientProfile)


async def create_domain(domain_name: str):
    req = models.CreateDomainRequest()
    params = {
        "Domain": domain_name
    }
    req.from_json_string(json.dumps(params))
    resp = client.CreateDomain(req)
    domain_result = json.loads(resp.to_json_string())
    domain_domain_info = domain_result['DomainInfo']
    domain_domain_info['GradeNsList'] = str(domain_domain_info.get('GradeNsList'))
    return domain_domain_info


async def delete_domain(domain_name: str):
    req = models.DeleteDomainRequest()
    params = {
        "Domain": domain_name
    }
    req.from_json_string(json.dumps(params))
    resp = client.DeleteDomain(req)
    return resp.to_json_string()


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


async def create_record(data):
    req = models.CreateRecordRequest()
    params = data
    req.from_json_string(json.dumps(params))
    resp = client.CreateRecord(req)
    return resp.to_json_string()


async def delete_record(domain_name: str, record_id: str):
    req = models.DeleteRecordRequest()
    params = {
        "Domain": domain_name,
        "RecordId": record_id
    }
    req.from_json_string(json.dumps(params))
    resp = client.DeleteRecord(req)
    return resp.to_json_string()


async def read_record(domain_name: str, record_id: str):
    req = models.DescribeRecordRequest()
    params = {
        "Domain": domain_name,
        "RecordId": record_id
    }
    req.from_json_string(json.dumps(params))
    resp = client.DescribeRecord(req)
    return resp.to_json_string()


async def update_record(domain_name: str, record_id: str, sub_domain_name: str, record_type: str, value: str):
    req = models.ModifyRecordRequest()
    params = {
        "Domain": domain_name,
        "RecordId": record_id,
        "SubDomain": sub_domain_name,
        "RecordType": record_type,
        "Value": value
    }
    req.from_json_string(json.dumps(params))
    resp = client.ModifyRecord(req)
    return resp.to_json_string()


