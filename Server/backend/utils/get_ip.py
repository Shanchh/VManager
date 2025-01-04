from fastapi import Request

def get_client_ip(request: Request) -> str:
    client_ip = request.headers.get("x-forwarded-for")
    if client_ip:
        return client_ip.split(",")[0].strip()
    return request.client.host