import sys
sys.path.append('../..')
from module.ssl.wild_card import create_wild_card
from module.dns.dns_pod import create_domain
import asyncio

# 建立域名
asyncio.run(create_domain('hqsmaxtest.online'))
# 申請萬用憑證
asyncio.run(create_wild_card('hqsmaxtest.online'))
