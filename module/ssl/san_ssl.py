import asyncio
import os
import shutil
from datetime import datetime, timedelta
import httpx


async def create_san_certificate(domains: list[str]):  # 修改參數為域名列表
    try:
        # 確認每個域名都指向正確的伺服器
        for domain in domains:
            print(domain)
            async with httpx.AsyncClient() as client:
                r = await client.get(f'http://{domain}/.well-known/acme-challenge/acme-pre-test', timeout=5)
                result_dict = r.json()
            if result_dict.get('message') != 'This is for acme pre-test':
                return {"message": f"域名 {domain} 尚未正確指向此伺服器"}

    except (httpx.RequestError, httpx.TimeoutException):
        return {"message": "此域名尚未正確指向此伺服器"}

    try:
        current_file_path = os.path.abspath(__file__)
        project_path = os.path.dirname(os.path.dirname(current_file_path))
        temp_ssl_path = os.path.join(project_path, 'ssl', 'temp')
        full_path = os.path.join(temp_ssl_path, domains[0])  # Use the first domain as the directory name
        challenge_route = os.path.join(temp_ssl_path, 'challenge_file')

        if not os.path.exists(full_path):
            os.makedirs(full_path)

        # 生成配置文件
        san_config = os.path.join(temp_ssl_path, f'san_{datetime.now().strftime("%Y%m%d%H%M%S")}.cnf')
        with open(san_config, 'w') as f:
            f.write("[ req ]\n")
            f.write("default_bits        = 2048\n")
            f.write("distinguished_name  = req_distinguished_name\n")
            f.write("req_extensions      = req_ext\n\n")
            f.write("[ req_distinguished_name ]\n")
            f.write(f"commonName          = {domains[0]}\n\n")
            f.write("[ req_ext ]\n")
            f.write("subjectAltName      = @alt_names\n\n")
            f.write("[alt_names]\n")
            for index, domain in enumerate(domains, start=1):
                f.write(f"DNS.{index} = {domain}\n")

        # 使用該配置文件來產生 CSR
        print(f'sudo openssl req -nodes -newkey rsa:2048 -sha256 -keyout {full_path}/privkey.key -out {full_path}/csr.csr -config {san_config}')
        await run_command(f'sudo openssl req -nodes -newkey rsa:2048 -sha256 -keyout {full_path}/privkey.key -out {full_path}/csr.csr -config {san_config}')

        # 刪除臨時的配置文件
        print(f'sudo rm {san_config}')
        await run_command(f'sudo rm {san_config}')

        # 產生所有的 -d 標記
        domain_flags = " ".join(f"-d {domain}" for domain in domains)

        # 使用所有的 -d 標記來簽名憑證請求
        print(f'~/.acme.sh/acme.sh --signcsr --csr {full_path}/csr.csr --webroot {challenge_route} {domain_flags} --fullchainpath {full_path}/fullchain.pem --force')
        await run_command(f'~/.acme.sh/acme.sh --signcsr --csr {full_path}/csr.csr --webroot {challenge_route} {domain_flags} --fullchainpath {full_path}/fullchain.pem --force')

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

        result = {
            "message": "success",
            "data": {
                "fullchain": fullchain,
                "privkey": privkey,
                "created_time": created_time,
                "expire_time": expire_time
            }
        }

        if full_path:
            shutil.rmtree(full_path)
            remove_path = f'~/.acme.sh/{domains[0]}'
            await run_command(f'sudo rm -rf {remove_path}')

        return result

    except Exception as e:
        return {"message": "fail", "data": str(e)}


async def run_command(cmd: str):
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        raise RuntimeError(f"'{cmd}' failed with error code {process.returncode}: {stderr.decode().strip()}")