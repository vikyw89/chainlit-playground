def run():
    import subprocess

    subprocess.run(args="chainlit run src/app.py -w", shell=True)