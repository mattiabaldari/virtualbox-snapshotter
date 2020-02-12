import os
import sys
import time
import virtualbox

from datetime import datetime
from vboxapi import VirtualBoxManager

vbox = virtualbox.VirtualBox()
session = virtualbox.Session()

def check_arguments():
    if len(sys.argv) < 2:
        print("Not enough argument provided")
        return 1
    elif not isinstance(sys.argv[1], str):
        print("Provided name is not istance of string")
        return 1
    return sys.argv[1]

def create_snapshot(machine_name=None):
    vm_initial_status = 1  # zero means powered on

    if machine_name:
        machine = vbox.find_machine(machine_name)
        if machine.state == virtualbox.library.MachineState(1):  # MachineState(1) = PowerOff
            vm_initial_status = 0
            proc = machine.launch_vm_process(session, "headless")
            proc.wait_for_completion(timeout=-1)

        snap_name = datetime.now().strftime("%d-%m-%Y")
        description = "Daily Snapshot " + datetime.now().strftime("%d-%m-%Y")
        
        if vm_initial_status:
            shared_lockType = virtualbox.library.LockType(1)
            machine.lock_machine(session, shared_lockType)

        process, unused_variable = session.machine.take_snapshot(snap_name, description, False)
        process.wait_for_completion(timeout=-1)
    else:
        print("machine_name is None")
    
    return vm_initial_status
    
def main():
    name = check_arguments()
    vm_status = create_snapshot(name)

    if not vm_status:
        session.console.power_down()
    session.unlock_machine()


if __name__ == "__main__":
    main()
