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

def delete_last_snapshot(machine_name=None):

    if machine_name:
        virtual_machine = vbox.find_machine(machine_name)
        try:
            root_snapshot = virtual_machine.find_snapshot("")
            child_id_name = [ str(), str() ]
            for child in root_snapshot.children:
                children = virtual_machine.find_snapshot(child.name)
                child_id_name[0] = children.id_p
                child_id_name[1] = children.name
            virtual_machine.lock_machine(session, virtualbox.library.LockType(1))
            
            process = session.machine.delete_snapshot(child_id_name[0])
            process.wait_for_completion(timeout=-1)
            #if machine.session_state == virtualbox.library.SessionState(2):  # SessionState(2) = Locked
            #    if session.state == virtualbox.library.SessionState(2):
            #        session.unlock_machine()
            print("Deleted " + child_id_name[1])
        except:
            print("Delete " + machine_name + " snapshot failed")
            return
    else:
        print("machine_name is None")

def create_snapshot(machine_name=None):
    vm_initial_status = 1  # zero means powered on

    if machine_name:
        machine = vbox.find_machine(machine_name)
        if machine.state == virtualbox.library.MachineState(1):  # MachineState(1) = PowerOff
            vm_initial_status = 0
            if session.state == virtualbox.library.SessionState(2):
                session.unlock_machine()
            proc = machine.launch_vm_process(session, "headless")
            proc.wait_for_completion(timeout=-1)

        snap_name = datetime.now().strftime("%d-%m-%Y")
        description = "Daily Snapshot " + datetime.now().strftime("%d-%m-%Y")
        
        if vm_initial_status:
            if machine.session_state == virtualbox.library.SessionState(2):  # SessionState(2) = Locked
                # The first IF check wheter the machine is in locked session, the second one checks if
                # the session is locked
                if session.state == virtualbox.library.SessionState(2):
                    session.unlock_machine()
            shared_lockType = virtualbox.library.LockType(1)
            machine.lock_machine(session, shared_lockType)

        process, unused_variable = session.machine.take_snapshot(snap_name, description, False)
        process.wait_for_completion(timeout=-1)
        print("Created: " + description)
        
        if vm_initial_status:
            if session.state == virtualbox.library.SessionState(2):
                session.unlock_machine()
    else:
        print("machine_name is None")
    
    return vm_initial_status
    
def main():
    print("Starting autosnapshotter script ...")
    name = check_arguments()
    delete_last_snapshot(name)
    vm_status = create_snapshot(name)

    if not vm_status:
        session.console.power_down()

if __name__ == "__main__":
    main()
