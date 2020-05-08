import os
import urllib.request as urlreq
from subprocess import Popen, PIPE
import zipfile

# Does not work because it's apparently not a zip file
zippath = "julius.zip"
urlreq.urlretrieve("http://www.sppas.org/downloads/julius.zip", zippath)
zf = zipfile.ZipFile(zippath, "r")
listOfFileNames = zf.namelist()
for fileName in listOfFileNames:
    if fileName == "julius/julius-4.3.1.exe":
        zf.extract(fileName, "../bin")
zf.close()
os.remove(zippath)

Popen("move julius\\julius-4.3.1.exe .", stdout=PIPE, stderr=PIPE, shell=True)
Popen("rmdir julius", stdout=PIPE, stderr=PIPE, shell=True)
Popen("rename julius-4.3.1.exe julius.exe", stdout=PIPE, stderr=PIPE, shell=True)
# t = Popen("move julius.exe C:\\", stdout=PIPE, stderr=PIPE, text=True, shell=True)

