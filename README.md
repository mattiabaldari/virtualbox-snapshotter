# virtualbox-snapshotter
Python script to automatize the Virtualbox snapshot process

# Installation process
Youtube Guide: https://www.youtube.com/watch?v=uDEFQyu4MvM
 
In order to function, this script requires the following step to be performed:

**1. Install the VirtualBox SDK:** 
Go to VirtualBox’s downloads page (https://www.virtualbox.org/wiki/Downloads) and download the VirtualBox SDK. Within the extracted ZIP file there is a directory called “installer”. Open a console within the installer directory and, using your system Python 3, run: 
```
python vboxapisetup.py install 
```


**2. Install the requirements file:**
```
python -m pip install -r requirements.txt
```

Finished! 


How to run:
```
python main.py "virtual_machine_name"
```
