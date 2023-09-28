import sys
sys.path.append('../..')
from module.ssl.single_ssl import create_certificate
from module.dns.dns_pod import create_record
import asyncio


data_template = {
    "Domain": "hqsmaxtest.online",
    "SubDomain": "test",
    "RecordType": "CNAME",
    "RecordLine": "默认",
    "Value": "test1.hqsmaxtest.online"
}
#
# tasks = []
#
for i in range(10):
    data = data_template.copy()
    data["SubDomain"] = f"cnametest{i}"
    asyncio.run(create_record(data))


for i in range(10):
    # create_certificate(f"cnametest{i}.hqsmaxtest.online")
    asyncio.run(create_certificate(f"cnametest{i}.hqsmaxtest.online"))

