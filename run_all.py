import asyncio
import signal
import os
import sys

BOTS = [
    {"name": "FBAIKadroBot", "cmd": [sys.executable, "main.py"], "dir": "FBAIKadroBot"},
    {"name": "FBAITahminBot", "cmd": [sys.executable, "main.py"], "dir": "FBAITahminBot"},
    {"name": "FBBot", "cmd": [sys.executable, "main.py"], "dir": "FBBot"},
    {"name": "FBLevelBot", "cmd": [sys.executable, "main.py"], "dir": "FBLevelBot"},
    {"name": "FBTicketBot", "cmd": [sys.executable, "bot.py"], "dir": "FBTicketBot"},
    {"name": "FBYayinBot", "cmd": [sys.executable, "main.py"], "dir": "FBYayinBot"},
]

processes = []

def get_env():
    return os.environ.copy()

async def run_bot(bot_info):
    name = bot_info["name"]
    cwd = os.path.join(os.path.dirname(os.path.abspath(__file__)), bot_info["dir"])
    env = get_env()
    while True:
        print(f"[{name}] Başlatılıyor...")
        proc = await asyncio.create_subprocess_exec(
            *bot_info["cmd"],
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            env=env,
        )
        processes.append(proc)
        async for line in proc.stdout:
            print(f"[{name}] {line.decode().rstrip()}")
        rc = await proc.wait()
        print(f"[{name}] Çıktı (kod: {rc}), 5 saniye sonra yeniden başlatılıyor...")
        await asyncio.sleep(5)

async def main():
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: [p.terminate() for p in processes])
    tasks = [asyncio.create_task(run_bot(bot)) for bot in BOTS]
    print(f"{len(BOTS)} bot başlatılıyor...")
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
