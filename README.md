# virtualbox-snapshotter
Python script to automatize the Virtualbox snapshot process

## Installation process
Youtube Guide: https://www.youtube.com/watch?v=uDEFQyu4MvM
 
### Install
In order to function, this script requires the following step to be performed:

**1. [Install the VirtualBox SDK](VirtualBox-SDK/README.md)** 

**2. Download the project zip and unpack it**

**3. Open a CMD terminal and go into the project directory**

**4. Install the requirements file:**
```
python -m pip install -r requirements.txt
```
Remember to run the installation command from within the project directory:
![](guide-images/requirements.png?raw=true "Requirements")


----------------------------------------

### Run

The installation process is over. To run the script:
```
python main.py "name_of_your_virtualbox_vm"
```

----------------------------------------
### Schedule

In order to automatize the backup process use the following guides:

* [[Win-10] Task scheduler](https://www.windowscentral.com/how-create-automated-task-using-task-scheduler-windows-10)

* [[Linux] Crontab](https://askubuntu.com/questions/2368/how-do-i-set-up-a-cron-job)

----------------------------------------
### Notes

* **Deletion error**
 
    The first time you run the script it could raise an error in the deletion phase.
    That's normal if you do not have any snapshot, therefore nothing to delete.
    Don't pay attention to it, it will disappear from the second run on.
    
* **Snapshot retention**
    The script deletes and creates a snapshot every time it runs.
    Therefore if the VM has 2 snapshots (or more) at the run 
    moment, then the VM will continue to have 2 snapshots.
    The only exception is when the VM has no snapshots and the script 
    produce the first of them.