To Install the VirtualBox SDK: 

**1. Go to VirtualBox’s download [page](https://www.virtualbox.org/wiki/Downloads) 
and download it:** 
![Screenshot of the correct link to download](guide-images/VirtualBox-SDK.png?raw=true "Link")

**2. Extract the content **

**3. Open a CMD session and place yourself within the folder "sdk/installer"**
![Screenshot of the installer path](guide-images/cmd.png?raw=true "Cmd")

Within the extracted ZIP file there is a directory called “installer”. Open a console within the installer directory and, using your system Python 3, run: 
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
