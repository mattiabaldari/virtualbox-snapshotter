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
            idx = 0
            #children = root_snapshot.children
            current_snapshot = root_snapshot
            first_snapshot = list()
            last_snapshot = str()

            while True:
                children = current_snapshot.children
                for child in children:
                    snapshot_child = virtual_machine.find_snapshot(child.id_p)
                if idx == 0:
                    first_snapshot = snapshot_child.id_p, snapshot_child.name
                    idx += 1
                last_snapshot = snapshot_child.id_p
                if snapshot_child.children_count == 0:
                    break
                current_snapshot = snapshot_child

            if first_snapshot[0] != last_snapshot:
                virtual_machine.lock_machine(session, virtualbox.library.LockType(1))
                process = session.machine.delete_snapshot(first_snapshot[0])
                process.wait_for_completion(timeout=-1)
                print("Deleted " + first_snapshot[1])
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
