# Download an install julius for Windows

import sys
if sys.version_info < (3, 6):
    print("The version of Python is too old: "
          "This program requires at least version 3.6.")
    sys.exit(1)
if sys.platform != "win32":
    print("This program is dedicated 'win32' systems. Current system is {}"
          "".format(sys.platform))
    sys.exit(1)

import os
import urllib.request as urlreq
from subprocess import Popen, PIPE
import zipfile

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))

# Download the zip file with Julius executable file
# -------------------------------------------------

zip_path = "julius.zip"
urlreq.urlretrieve("http://www.sppas.org/downloads/julius.zip", zip_path)
if os.path.exists(zip_path) is False:
    print("Julius zip package can't be downloaded.")
    sys.exit(10)

# Extract the executable file
# -------------------------------------------------

zf = zipfile.ZipFile(zip_path, "r")
zipped_files = zf.namelist()
julius_filename = ""
for filename in zipped_files:
    fn = os.path.basename(filename)
    if fn.startswith("julius") and fn.endswith(".exe"):
        julius_filename = filename
        zf.extract(filename, SPPAS)
zf.close()
if julius_filename == "":
    print("Julius executable not found in zip.")
    sys.exit(20)
# we don't need the zip file anymore
os.remove(zip_path)


# Move Julius executable to SPPAS and rename
# -------------------------------------------------
julius_filename = julius_filename.replace("/", "\\")

command = "move "
command += julius_filename
command += " .\\julius.exe"
process = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
process.wait()

if os.path.exists(os.path.join(SPPAS, "julius.exe")) is False:
    print("Julius executable {} cant't be moved to SPPAS directory."
          "".format(os.path.join(SPPAS, julius_filename)))
    sys.exit(30)

# we don't need the zip directory anymore
command = "rmdir julius"
Popen(command, stdout=PIPE, stderr=PIPE, shell=True)


# Move Julius executable to c:\\Windows
# -------------------------------------------------

command = "move"
command += " .\\julius.exe"
command += " C:\\WINDOWS"

try:
    Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
    process.wait()
except Exception as e:
    print(str(e))

if os.path.exists("c:\\windows\\julius.exe") is False:
    print("Julius executable file can't be moved to C:\\Windows.")
    print("You probably don't have administrative rights.")
    sys.exit(40)

# we don't need the exe file anymore
os.remove(os.path.join(SPPAS, "julius.exe"))

sys.exit(0)
