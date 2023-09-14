import asyncio
import os
from datetime import datetime, timedelta
import requests


async def create_certificate(domain: str):
    try:
        # test_result = requests.get(f'http://{domain}/.well-known/acme-challenge/test').text
        # if test_result != 'success':
        #     return {"message": "此域名尚未正確指向此伺服器"}
        current_file_path = os.path.abspath(__file__)
        project_path = os.path.dirname(os.path.dirname(current_file_path))
        temp_ssl_path = os.path.join(project_path, 'ssl', 'temp')
        full_path = os.path.join(temp_ssl_path, domain)
        challenge_route = os.path.join(temp_ssl_path, 'challenge_file')
        if not os.path.exists(full_path):
            os.makedirs(full_path)
        await run_command(f'sudo openssl req -nodes -newkey rsa:2048 -sha256 -keyout {full_path}/privkey.key -out {full_path}/csr.csr -subj "/CN={domain}"')
        await run_command(f'sudo chmod -R 777 {full_path}')
        await run_command(f'~/.acme.sh/acme.sh --signcsr --csr {full_path}/csr.csr --webroot {challenge_route} -d {domain} --fullchainpath {full_path}/fullchain.pem --force')
        for i in range(5):
            if os.path.exists(os.path.join(full_path, 'fullchain.pem')) and os.path.exists(os.path.join(full_path, 'privkey.key')):
                break
            await asyncio.sleep(2)
        with open(os.path.join(full_path, 'fullchain.pem'), 'r') as f:
            fullchain = f.read()
        with open(os.path.join(full_path, 'privkey.key'), 'r') as f:
            privkey = f.read()
        created_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        expire_time = (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d %H:%M:%S")
        # 移除相關檔案
        # await run_command(f'rm -rf {full_path}')
        return {"message": "success", "fullchain": fullchain, "privkey": privkey, "created_time": created_time, "expire_time": expire_time}
    except Exception as e:
        return {"message": f"error: {e}"}


async def get_certificate(domain: str):
    try:
        current_file_path = os.path.abspath(__file__)
        project_path = os.path.dirname(os.path.dirname(current_file_path))
        temp_ssl_path = os.path.join(project_path, 'ssl', 'temp')
        full_path = os.path.join(temp_ssl_path, domain)
        if not os.path.exists(full_path):
            return {"message": "此域名尚未申請"}
        with open(os.path.join(full_path, 'fullchain.pem'), 'r') as f:
            fullchain = f.read()
        with open(os.path.join(full_path, 'privkey.key'), 'r') as f:
            privkey = f.read()
        return {"fullchain": fullchain, "privkey": privkey}
    except Exception as e:
        return {"message": f"error: {e}"}


async def run_command(cmd: str):
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        raise RuntimeError(f"'{cmd}' failed with error code {process.returncode}: {stderr.decode().strip()}")