# utils/auth.py
# demo auth - in hackathon this is enough; replace with real auth in production
USERS = {
    "admin": {"password": "adminpass", "role": "admin"},
    "user": {"password": "userpass", "role": "user"}
}

def authenticate(username, password):
    u = USERS.get(username)
    if not u: return None
    if u["password"] == password:
        return {"username": username, "role": u["role"]}
    return None