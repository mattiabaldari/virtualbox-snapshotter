# virtualbox-snapshotter
Python script to automatize the Virtualbox snapshot process

# Installation process
In order to function, this script requires the following step to be performed:
**1. Install the VirtualBox SDK:** 
Go to VirtualBox’s downloads page (https://www.virtualbox.org/wiki/Downloads) and download the VirtualBox SDK. Within the extracted ZIP file there is a directory called “installer”. Open a console within the installer directory and, using your system Python 3, run: 
```
python vboxapisetup.py install 
```


**2. Install the virtualbox python package:**
```
python -m pip install virtualbox
```
**3. Install the pywin32 python package:**
```
python -m pip install pywin32
```
**4. Install the following library: https://pypi.org/project/pyvbox/**

Finished!


How to run:
```
python main.py "virtual_machine_name"
```
