import os
import asyncio
import shutil
from datetime import datetime, timedelta


async def create_wild_card(domain: str):
    try:
        current_file_path = os.path.abspath(__file__)
        project_path = os.path.dirname(os.path.dirname(current_file_path))
        temp_ssl_path = os.path.join(project_path, 'ssl', 'temp')
        full_path = os.path.join(temp_ssl_path, domain)
        if not os.path.exists(full_path):
            os.makedirs(full_path)
        await run_command(f"openssl req -nodes -newkey rsa:2048 -sha256 -keyout {full_path}/privkey.key -out {full_path}/csr.csr -subj '/CN=*.{domain}'")
        await run_command(f"chmod -R 777 {full_path}")
        timeout_seconds = 120  # for example, 2 minutes
        await asyncio.wait_for(run_command(f" ~/.acme.sh/acme.sh --signcsr --csr {full_path}/csr.csr --dns dns_dpi -d {domain} --fullchainpath {full_path}/fullchain.pem --force"),timeout_seconds)
        for i in range(5):
            if os.path.exists(os.path.join(full_path, 'fullchain.pem')) and os.path.exists(os.path.join(full_path, 'privkey.key')):
                break
            await asyncio.sleep(2)
        with open(os.path.join(full_path, 'fullchain.pem'), 'r') as f:
            fullchain = f.read()
        with open(os.path.join(full_path, 'privkey.key'), 'r') as f:
            privkey = f.read()
        create_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        expire_time = (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d %H:%M:%S')
        result = {
            "message": "success",
            "data": {
                "fullchain": fullchain,
                "privkey": privkey,
                "create_time": create_time,
                "expire_time": expire_time
            }
        }

        if full_path:
            shutil.rmtree(full_path)
            remove_path = f'~/.acme.sh/{domain}'
            await run_command(f'sudo rm -rf {remove_path}')
        print(result)
        return result
    except asyncio.TimeoutError:
        print("Command execution took too long!")
        return {"message": "fail", "data": "Command execution took too long!"}
    except Exception as e:
        print({"message": "fail", "data": str(e)})
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