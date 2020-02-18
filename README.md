# virtualbox-snapshotter
Python script to automatize the Virtualbox snapshot process

# Installation process
Youtube Guide: https://www.youtube.com/watch?v=uDEFQyu4MvM
 
In order to function, this script requires the following step to be performed:

**1. [Install the VirtualBox SDK](VirtualBox-SDK/README.md)** 


**2. Once the SDK installation is over install the requirements file:**
```
python -m pip install -r requirements.txt
```
Remember to run the installation command from within the project directory:
![](guide-images/requirements.png?raw=true "Requirements")


The installation process is over. To run the script:
```
python main.py "name_of_your_virtualbox_vm"
```
