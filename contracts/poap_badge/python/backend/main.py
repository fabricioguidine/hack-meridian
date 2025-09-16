import ctypes
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import ctypes

# Caminho para a biblioteca Rust compilada
lib_path = os.path.abspath("../../../../target/release/libpoap_badge.dylib")
lib = ctypes.CDLL(lib_path)

# Exemplo: função add
lib.add.argtypes = [ctypes.c_ulonglong, ctypes.c_ulonglong]
lib.add.restype = ctypes.c_ulonglong
print("Soma:", lib.add(2, 3))

# Exemplo: função list_user_badges (adaptado para receber um inteiro como user_id)
lib.list_user_badges.argtypes = [ctypes.c_ulonglong]
lib.list_user_badges.restype = ctypes.c_ulonglong
print("Badges do usuário:", lib.list_user_badges(42))

app = FastAPI()

class Badge(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    owner: Optional[str] = None

badges_db = []

# Endpoint que usa a função add da lib Rust
@app.get("/add")
def add_endpoint(left: int, right: int):
    result = lib.add(left, right)
    return {"result": result}

# Endpoint que usa a função list_user_badges da lib Rust
@app.get("/user_badges/{user_id}")
def user_badges_endpoint(user_id: int):
    badge_count = lib.list_user_badges(user_id)
    return {"user_id": user_id, "badge_count": badge_count}

@app.get("/badges", response_model=List[Badge])
def list_badges():
    return badges_db

@app.post("/badges", response_model=Badge)
def create_badge(badge: Badge):
    badges_db.append(badge)
    return badge

@app.get("/badges/{badge_id}", response_model=Badge)
def get_badge(badge_id: int):
    for badge in badges_db:
        if badge.id == badge_id:
            return badge
    raise HTTPException(status_code=404, detail="Badge not found")

@app.put("/badges/{badge_id}", response_model=Badge)
def update_badge(badge_id: int, badge: Badge):
    for i, b in enumerate(badges_db):
        if b.id == badge_id:
            badges_db[i] = badge
            return badge
    raise HTTPException(status_code=404, detail="Badge not found")

@app.delete("/badges/{badge_id}")
def delete_badge(badge_id: int):
    for i, b in enumerate(badges_db):
        if b.id == badge_id:
            del badges_db[i]
            return {"detail": "Badge deleted"}
    raise HTTPException(status_code=404, detail="Badge not found")
