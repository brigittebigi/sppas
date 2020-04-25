import os
import urllib.request as urlreq
from zipfile import ZipFile
import zipfile

print('Beginning file download with urllib2...')

# Works because it's apparently a zip file
zippath = os.path.join(os.getcwd(), "mnist.zip")
urlreq.urlretrieve("http://data.mxnet.io/mxnet/data/mnist.zip", zippath)
zf = zipfile.ZipFile(zippath, "r")
listOfFileNames = zf.namelist()
for fileName in listOfFileNames:
    if fileName == "t10k-images-idx3-ubyte":
        zf.extract("t10k-images-idx3-ubyte")
zf.close()
os.remove(zippath)

# Does not work because it's apparently not a zip file, but I create it with the link so I don't understand at all why
# zippath = os.path.join(os.getcwd(), "essai.zip")
# urlreq.urlretrieve("https://mega.nz/file/BjJg0KbT", zippath)
# zf = zipfile.ZipFile(zippath, "r")
# zf.extractall("bin/essai.jpg")
# zf.close()
# os.remove(zippath)

# Does not work because it's apparently not a zip file
# zippath = os.path.join(os.getcwd(), "julius-4.3.1-win32bin.zip")
# urlreq.urlretrieve("http://sourceforge.jp/projects/julius/downloads/60273/julius-4.3.1-win32bin.zip", zippath)
# zf = zipfile.ZipFile(zippath, "r")
# zf.extractall("bin/julius-4.3.1.exe")
# zf.close()
# os.remove(zippath)
