# virtualbox-snapshotter
Python script to automatize the Virtualbox snapshot process

# Installation process
Youtube Guide: https://www.youtube.com/watch?v=uDEFQyu4MvM
 
In order to function, this script requires the following step to be performed:

**1. [Install the VirtualBox SDK](VirtualBox-SDK/README.md)** 

**2. Download the project zip and unpack it**

**3. Open a CMD terminal and go into the project directory**

**3.  install the requirements file:**
```
python -m pip install -r requirements.txt
```
Remember to run the installation command from within the project directory:
![](guide-images/requirements.png?raw=true "Requirements")


The installation process is over. To run the script:
```
python main.py "name_of_your_virtualbox_vm"
```


**In order to automatize the backup process use the following guides:**

* [[Win-10] Task scheduler]([https://www.windowscentral.com/how-create-automated-task-using-task-scheduler-windows-10](https://www.windowscentral.com/how-create-automated-task-using-task-scheduler-windows-10))

* [[Linux] Crontab](https://askubuntu.com/questions/2368/how-do-i-set-up-a-cron-job)