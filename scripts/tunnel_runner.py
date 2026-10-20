import os
import re
import subprocess
import sys
import time

def find_cloudflared():
    paths = [
        r"C:\Program Files (x86)\cloudflared\cloudflared.exe",
        r"C:\Program Files\cloudflared\cloudflared.exe",
        "cloudflared"
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return "cloudflared"

def main():
    print("=" * 65)
    print("      QUANTGOLD OS - PUBLIC LAUNCHER (MOBILE ACCESSIBLE)")
    print("=" * 65)
    
    # 1. Start backend server
    print("[1/2] Starting QuantGold Server on port 8000...")
    backend_proc = subprocess.Popen(
        [sys.executable, "run_server.py"],
        cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(2)

    # 2. Start Cloudflare Quick Tunnel
    cf_bin = find_cloudflared()
    print(f"[2/2] Launching Cloudflare Public Tunnel via {cf_bin}...")
    tunnel_proc = subprocess.Popen(
        [cf_bin, "tunnel", "--url", "http://localhost:8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    public_url = None
    url_pattern = re.compile(r"https://[a-zA-Z0-9\-]+\.trycloudflare\.com")

    # Read output to capture public URL
    start_time = time.time()
    while time.time() - start_time < 30:
        line = tunnel_proc.stdout.readline()
        if not line:
            continue
        match = url_pattern.search(line)
        if match:
            public_url = match.group(0)
            break

    if public_url:
        print("\n" + "#" * 65)
        print("  SUCCESS! QUANTGOLD IS LIVE & ACCESSIBLE WORLDWIDE:")
        print(f"  --> {public_url} <--")
        print("#" * 65)
        print("\nCara Buka di HP Jibran:")
        print(f"1. Kirim link ini ke WhatsApp Jibran: {public_url}")
        print("2. Jibran buka link di Google Chrome HP Android.")
        print("3. Tekan menu titik-tiga (⋮) di Chrome -> pilih 'Install App' / 'Add to Home Screen'.")
        print("4. QuantGold akan langsung terpasang sebagai aplikasi mandiri di HP Jibran!")
        print("\nTekan Ctrl+C untuk mematikan server & tunnel.\n")
    else:
        print("\nLocal server running on http://localhost:8000")
        print("Could not auto-detect Cloudflare public URL. Check internet connection.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down QuantGold engine and tunnel...")
        tunnel_proc.terminate()
        backend_proc.terminate()
        print("Shutdown complete.")

if __name__ == '__main__':
    main()
