# import subprocess

# proc = subprocess.Popen("py", stdin=subprocess.PIPE, stdout=subprocess.PIPE)

# proc.stdin.write(b"a=0")
# proc.stdin.write(b"a")
# print(proc.stdout.read().decode())
# import asyncio


# async def run(cmd="py"):
#     proc = await asyncio.create_subprocess_shell(
#         cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
#     )
#     stdout, stderr = await proc.communicate(input=b"a=0")
#     stdout, stderr = await proc.communicate(b"a")
#     print(stdout)


# asyncio.run(run())
import asyncio


async def run(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await proc.communicate(b"a=0")

    print(f"[{cmd!r} exited with {proc.returncode}]")
    if stdout:
        print(f"[stdout]\n{stdout.decode()}")
    if stderr:
        print(f"[stderr]\n{stderr.decode()}")


asyncio.run(run("py"))
