from datetime import datetime
import argparse

import virtualbox

vbox = virtualbox.VirtualBox()
session = virtualbox.Session()


def delete_oldest_snapshots(machine_name: str, number_to_retain: int) -> None:
    """
    Attempts to delete oldests snapshots from specified machine.

    in machine_name of type str
        Machine name to search for.

    in number_to_retain of type int
        Number of newest snapshots to retain.

    """
    try:
        # Trying to find a machine
        virtual_machine = vbox.find_machine(machine_name)

        # Snapshot ids[0] and names[1] sorted from oldest (index - 0) to newest (index - higest)
        snapshot_details = []
        # Getting root snapshot and adding it to a list
        snapshot = virtual_machine.find_snapshot("")
        snapshot_details.append([snapshot.id_p, snapshot.name])

        # Traversing through children snapshots (until one has no children) and adding them to a list
        while snapshot.children_count != 0:
            # TODO: Implement multi children scan
            # This check skips snapshot marked as "Current State"
            snapshot = snapshot.children[0]
            snapshot_details.append([snapshot.id_p, snapshot.name])

        print("Overall list of snapshot:")
        for snapshot in snapshot_details:
            print(f"Snapshot ID: {snapshot[0]} Name: {snapshot[1]}")

        if number_to_retain > len(snapshot_details):
            print("Number of snapshots to be retained is bigger then number of available snapshots. \
                  Snapshot deletion aborted.")
            return

        # Removing number of snapshots from the list of snapshots to be deleted
        snapshot_details = snapshot_details[:len(snapshot_details) - number_to_retain]
        print("List of snapshots to be deleted:")
        if len(snapshot_details) == 0:
            # In case all existing snapshots to be retained
            print("None")
            return

        for snapshot in snapshot_details:
            print(f"Snapshot ID: {snapshot[0]} Name: {snapshot[1]}")

        # Locking VM
        virtual_machine.lock_machine(session, virtualbox.library.LockType(1))
        for snapshot in snapshot_details:
            # Deleting snapshot by using Snapshot ID
            process = session.machine.delete_snapshot(snapshot[0])
            print(f"Deleting {snapshot[1]}...")
            process.wait_for_completion(timeout=-1)
            print(f"Deleted {snapshot[1]}")
    except Exception as ex:
        print(f"Snapshot deletion aborted prematurely due to following exception: {ex}")


def create_snapshot(machine_name: str) -> bool:
    """
    Attempts to create a snapshot for specified machine.

    in machine_name of type str
        Machine name to search for.

    return vm_running_initally of type bool
        Status if machine was in any state but "Powered Off" initally
    """
    # Assuming that machine is initally in any state but not in "Powered Off"
    vm_running_initally = True

    virtual_machine = vbox.find_machine(machine_name)
    if virtual_machine.state == virtualbox.library.MachineState(1):
        # Check if machine is powered off (MachineState(1) = PowerOff)
        vm_running_initally = False

        if session.state == virtualbox.library.SessionState(2):
            # Check if session is locked (SessionState(2) = Locked)
            session.unlock_machine()

        # Locks virtual machine from writes
        proc = virtual_machine.launch_vm_process(session, "headless", [])
        proc.wait_for_completion(timeout=-1)

    # Creating snapshot name and description
    snap_name = "Regular Snapshot " + datetime.now().strftime("%d-%m-%Y")
    description = "Regular Snapshot taken on " + datetime.now().strftime("%d-%m-%Y") + " via virtualbox-snapshotter"

    if vm_running_initally:
        # Check if inital state of a machine was anything but "Powered Off"
        if virtual_machine.session_state == virtualbox.library.SessionState(2):
            # Check if VM session is locked (SessionState(2) = Locked)
            if session.state == virtualbox.library.SessionState(2):
                # Check if current session is locked (SessionState(2) = Locked)
                session.unlock_machine()

        # Locking machine to allow making changes
        shared_lock_type = virtualbox.library.LockType(1)
        virtual_machine.lock_machine(session, shared_lock_type)

    # Taking snapshot
    process, _ = session.machine.take_snapshot(snap_name, description, False)
    process.wait_for_completion(timeout=-1)

    print("Created: " + snap_name)

    if vm_running_initally:
        # Check if inital state of a machine was anything but "Powered Off"
        if session.state == virtualbox.library.SessionState(2):
            # Check if session is locked
            session.unlock_machine()

    return vm_running_initally


def main():
    parser = argparse.ArgumentParser(prog="VirtualBox Snapshotter",
                                     description="Takes new snapshots and deletes old ones\
                                        for specified Virtual Machine.",
                                     epilog="Currently, multi children are not supported.\
                                        Nested children are supported.")
    parser.add_argument("-m", "--machine-name",
                        action="store",
                        help="(Required) Virtual Machine (VM) name enclosed in double quotes (\").\
                            Not using double quotes may lead to abnormal behaviour if name contains whitespaces.",
                        metavar="\"VM_NAME\"",
                        type=str,
                        required=True
                        )
    parser.add_argument("-r", "--retain",
                        action="store",
                        choices=range(0, 1000),
                        default=3,
                        help="Number of latest snapshots to retain.\
                              If 0 is provided - deletes all snapshots leaving just the Currrent State one.\
                              If argument is not provided, defaults to 3.",
                        metavar="(0-1000)",
                        type=int,
                        required=False,
                        )
    args = parser.parse_args()

    print("Starting autosnapshotter script ...")
    delete_oldest_snapshots(args.machine_name, args.retain)
    vm_status = create_snapshot(args.machine_name)

    if not vm_status:
        session.console.power_down()


if __name__ == "__main__":
    main()
