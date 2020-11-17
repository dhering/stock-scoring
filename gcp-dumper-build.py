import os
import zipfile

if not os.path.isdir("dist"):
    os.mkdir("dist")

zf = zipfile.ZipFile("dist/gcp-dumper-function.zip", "w")
for dirname, subdirs, files in os.walk("libs"):
    if not dirname.endswith("__pycache__"):
        zf.write(dirname)
        for filename in files:
            zf.write(os.path.join(dirname, filename))

zf.write("gcp-dumper-function.py", "main.py")
zf.write("requirements.txt")

zf.close()