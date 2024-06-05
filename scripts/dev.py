def run():
    import subprocess
    import asyncio

    subprocess.run(args="chainlit run src/app.py", shell=True)