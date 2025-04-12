from fastapi import FastAPI, Request
#from parse import parse
import aiohttp
import uvicorn
import re

# === CONFIGURATION ===

HA_URL = "http://localhost:8123"
HA_TOKEN = "API_KEY"

# États cibles
STATE_ON = "checked out"
STATE_OFF = "checked in"

# === APP FASTAPI ===

app = FastAPI()

async def set_switch(state: str, id: str):
    url = f"{HA_URL}/api/services/switch/turn_{state}"
    headers = {
        "Authorization": f"Bearer {HA_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {"entity_id": f"switch.asset_{id}"}
    print(f"switch.asset_{id}")

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            response.raise_for_status()
            print(f"[HA] switch.switch.asset_{id} -> {state}")

@app.post("/webhook")
async def receive_webhook(request: Request):
    payload = await request.json()
    #print(f"[Webhook reçu] ID : {payload}")

    try:
        title_link = payload["attachments"][0]["title_link"]  # ex: http://.../hardware/1
        match = re.search(r"/hardware/(\d+)", title_link)
        if match:
            hardware_id = match.group(1).zfill(5)

            print(f"[INFO] Hardware ID : {hardware_id}")

            if payload.get("text", {}).find(STATE_ON) != -1:
                await set_switch("on", hardware_id)
                print("[Webhook reçu] Nouveau statut : checked out")
            elif payload.get("text", {}).find(STATE_OFF) != -1:
                await set_switch("off", hardware_id)
                print("[Webhook reçu] Nouveau statut : checked in")
            else:
                print("[INFO] Statut ignoré")
        else:
            print("[ERREUR] ID non trouvé dans title_link")
            return {"status": "erreur"}
    except Exception as e:
        print(f"[ERREUR] Webhook mal formé ou données manquantes : {e}")

    return {"status": "ok"}
