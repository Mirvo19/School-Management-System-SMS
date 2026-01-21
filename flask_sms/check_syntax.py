import compileall
import os

print("Checking syntax...")
try:
    compileall.compile_dir('app', force=True)
    print("Syntax check complete.")
except Exception as e:
    print(e)
