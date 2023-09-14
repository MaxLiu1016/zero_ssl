import asyncio
import os
# @app.get("/domain")
# async def domain():
#     try:
#         domain = 'test.hqsmaxtest.online'
#         current_file_path = os.path.abspath(__file__)
#         project_path = os.path.dirname(os.path.dirname(current_file_path))
#         temp_ssl_path = os.path.join(project_path, 'cname_ssl_v7', 'module', 'ssl', 'temp_ssl')
#         full_path = os.path.join(temp_ssl_path, domain)
#         if not os.path.exists(full_path):
#             os.makedirs(full_path)
#         await run_command(f'sudo openssl req -nodes -newkey rsa:2048 -sha256 -keyout {full_path}/privkey.key -out {full_path}/csr.csr -subj "/CN={domain}"')
#         print(f'sudo openssl req -nodes -newkey rsa:2048 -sha256 -keyout {full_path}/privkey.key -out {full_path}/csr.csr -subj "/CN={domain}"')
#         await run_command(f'sudo chmod -R 777 {full_path}')
#         print(f'acme.sh --signcsr --csr {full_path}/csr.csr --webroot {full_path} -d {domain} --fullchainpath {full_path}/fullchain.pem --force')
#         await run_command(f'acme.sh --signcsr --csr {full_path}/csr.csr --webroot {full_path} -d {domain} --fullchainpath {full_path}/fullchain.pem --force')
#         return {"message": "success"}
#     except Exception as e:
#         print(e)
#         return {"message": f"error: {e}"}


async def create_certificate(domain: str):
    try:
        test_result = await run_command(f'curl -I -X GET http://{domain}/.well-known/acme-challenge/test')
        if '200 OK' not in test_result:
            return {"message": "此域名尚未正確指向，請先指向後再申請"}
        current_file_path = os.path.abspath(__file__)
        project_path = os.path.dirname(os.path.dirname(current_file_path))
        temp_ssl_path = os.path.join(project_path, 'zero_ssl', 'module', 'ssl', 'temp_ssl')
        full_path = os.path.join(temp_ssl_path, domain)
        if not os.path.exists(full_path):
            os.makedirs(full_path)
        await run_command(f'sudo openssl req -nodes -newkey rsa:2048 -sha256 -keyout {full_path}/privkey.key -out {full_path}/csr.csr -subj "/CN={domain}"')
        await run_command(f'sudo chmod -R 777 {full_path}')
        await run_command(f'acme.sh --signcsr --csr {full_path}/csr.csr --webroot {full_path} -d {domain} --fullchainpath {full_path}/fullchain.pem --force')
        for i in range(5):
            if os.path.exists(os.path.join(full_path, 'fullchain.pem')) and os.path.exists(os.path.join(full_path, 'privkey.key')):
                break
            await asyncio.sleep(2)
        with open(os.path.join(full_path, 'fullchain.pem'), 'r') as f:
            fullchain = f.read()
        with open(os.path.join(full_path, 'privkey.key'), 'r') as f:
            privkey = f.read()
        created_time = await run_command(f'openssl x509 -in {full_path}/fullchain.pem -noout -startdate')
        expire_time = await run_command(f'openssl x509 -in {full_path}/fullchain.pem -noout -enddate')
        return {"message": "success", "fullchain": fullchain, "privkey": privkey, "created_time": created_time, "expire_time": expire_time}
    except Exception as e:
        return {"message": f"error: {e}"}


async def get_certificate(domain: str):
    try:
        current_file_path = os.path.abspath(__file__)
        project_path = os.path.dirname(os.path.dirname(current_file_path))
        temp_ssl_path = os.path.join(project_path, 'zero_ssl', 'module', 'ssl', 'temp_ssl')
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