import os
import uvicorn

if __name__ == "__main__":
    port_env = os.environ.get("PORT", "8000")
    try:
        cleaned_port = str(port_env).strip().strip("\"'").strip()
        port = int(cleaned_port)
    except (ValueError, TypeError):
        port = 8000

    print(f"🚀 Starting VajraNet Backend on 0.0.0.0:{port}...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, proxy_headers=True, forwarded_allow_ips="*")
