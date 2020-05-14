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
import shutil
import urllib.request as urlreq
import zipfile

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))

# Download the zip file with Julius executable file
# -------------------------------------------------

zip_path = "julius.zip"
urlreq.urlretrieve("http://www.sppas.org/downloads/julius.zip", zip_path)
if os.path.exists(zip_path) is False:
    sys.stderr.write("Julius zip package can't be downloaded.")
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
    sys.stderr.write("Julius executable not found in zip.")
    sys.exit(20)
# we don't need the zip file anymore
os.remove(zip_path)


# Move Julius executable to SPPAS and rename
# -------------------------------------------------
shutil.move(julius_filename, os.path.join(SPPAS, "julius.exe"))
if os.path.exists(os.path.join(SPPAS, "julius.exe")) is False:
    sys.stderr.write(
        "Julius executable {} cant't be moved to SPPAS directory."
        "".format(os.path.join(SPPAS, julius_filename)))
    sys.exit(30)

# we don't need the zip directory anymore
shutil.rmtree(os.path.join(SPPAS, "julius"))


# Move Julius executable to c:\\Windows
# -------------------------------------------------
julius_destination = os.path.join("C:", "Windows")
try:
    shutil.move(os.path.join(SPPAS, "julius.exe"), julius_destination)
except Exception as e:
    sys.stderr.write(str(e))

if os.path.exists(os.path.join(julius_destination, "julius.exe")) is False:
    sys.stderr.write("Julius executable file can't be moved to {dest}.\n"
                     "".format(dest=julius_destination))
    sys.stderr.write("You probably don't have administrative rights.")
    sys.exit(40)
else:
    # we don't need the exe file anymore
    os.remove(os.path.join(SPPAS, "julius.exe"))

sys.exit(0)
