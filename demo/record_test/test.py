import sys
sys.path.append('../..')
from module.ssl.wild_card import create_wild_card
from module.dns.dns_pod import create_record
import asyncio


data_template = {
    "Domain": "hqsmaxtest.online",
    "SubDomain": "test",
    "RecordType": "A",
    "RecordLine": "默认",
    "Value": "1.1.1.1"
}


for i in range(10):
    data = data_template.copy()
    data["SubDomain"] = f"recordtest{i}"
    asyncio.run(create_record(data))




