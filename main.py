import argparse
import virtualbox
from datetime import datetime

vbox = virtualbox.VirtualBox()
session = virtualbox.Session()

def delete_last_snapshot(machine_name):
    try:
        virtual_machine = vbox.find_machine(machine_name)
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
    except Exception as ex:
        print(f"Snapshot deletion exited prematurely with following exception: {ex}")
        return

def create_snapshot(machine_name):
    vm_initial_status = 1  # zero means powered on
    try:
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
    except Exception as ex:
        print(f"Snapshot creation exited prematurely with following exception: {ex}")
        # This will skip power down of machine on failure
        return 1
    
    return vm_initial_status
    
def main():
    parser = argparse.ArgumentParser(
                    prog = "VirtualBox Snapshotter",
                    description = "Takes new snapshot and deletes old one\
                    for specified Virtual Machine (VM).",
                    epilog="Get the latest release of VirtualBox Snapshotter from: https://github.com/Meru3m/virtualbox-snapshotter")
    parser.add_argument("vm_name",
                        action="store",
                        help="Virtual Machine (VM) name enclosed in double quotes (i.e. \"Awesome Virtual Machine\").\
                            Not using double quotes may lead to abnormal behaviour if name contains whitespaces.",
                        metavar="\"VM_NAME\"",
                        type=str
                        )
    args = parser.parse_args()
    print("Starting autosnapshotter script ...")
    delete_last_snapshot(args.vm_name)
    vm_status = create_snapshot(args.vm_name)

    try:
        if not vm_status:
            session.console.power_down()
    except Exception as ex:
        print(f"Power down of virtual machine execution exited prematurely with following exception: {ex}")
        return

if __name__ == "__main__":
    main()
