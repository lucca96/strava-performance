from src.client import StravaClient


def refresh_access_token(client=None):
    client = client or StravaClient()
    access_token = client.get_access_token()
    token_path = client.cache_dir / "token.json"
    token = client._read_json(token_path)
    return {
        "access_token": access_token,
        "refresh_token": token.get("refresh_token"),
        "expires_at": token.get("expires_at"),
    }
