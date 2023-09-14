import os
import asyncio


async def create_wild_card(domain: str):
    try:
        DNSPOD_ID = 'IKIDd6Ukrz59LfyKZouoeJtPq44sVxDG7qKc'
        DNSPOD_KEY = 'ACPSOEyb5NWTApQq8MoDWffhbKq8D5mK'
        current_file_path = os.path.abspath(__file__)
        project_path = os.path.dirname(os.path.dirname(current_file_path))
        temp_ssl_path = os.path.join(project_path, 'ssl', 'temp')
        full_path = os.path.join(temp_ssl_path, domain)
        if not os.path.exists(full_path):
            os.makedirs(full_path)
        await run_command(f"openssl req -nodes -newkey rsa:2048 -sha256 -keyout {full_path}/privkey.key -out {full_path}/csr.csr -subj '/CN=*.{domain}'")
        await run_command(f"chmod -R 777 {full_path}")
        await run_command(f"DP_Id='{DNSPOD_ID}' DP_Key='{DNSPOD_KEY}' ~/.acme.sh/acme.sh --signcsr --csr {full_path}/csr.csr --dns dns_dpi -d {domain} --fullchainpath {full_path}/fullchain.pem --force")
    except Exception as e:
        print(e)


async def run_command(cmd: str):
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        raise RuntimeError(f"'{cmd}' failed with error code {process.returncode}: {stderr.decode().strip()}")