from datetime import datetime
import argparse
import logging

import virtualbox

vbox = virtualbox.VirtualBox()
session = virtualbox.Session()

parser = argparse.ArgumentParser(prog="VirtualBox Snapshotter",
                                 description="Takes new snapshots and deletes old ones\
                                             for specified Virtual Machine.",
                                 epilog="Currently, multi children are not supported.\
                                        Nested children are supported.")
parser.add_argument("machine_name",
                    action="store",
                    help="(Required) Virtual Machine (VM) name enclosed in double quotes (\").\
                         Not using double quotes may lead to abnormal behaviour if name contains whitespaces.",
                    metavar="\"VIRTUAL_MACHINE_NAME\"",
                    type=str)

parser.add_argument("-r", "--retain",
                    action="store",
                    choices=range(0, 1000),
                    default=3,
                    help="Number of latest snapshots to retain.\
                         If 0 is provided - deletes all snapshots leaving just the latest one.\
                         If argument is not provided, defaults to 3.",
                    metavar="(0-1000)",
                    type=int,
                    required=False)

parser.add_argument("-v", "--verbose",
                    action="store_true",
                    help="Adds verbosity",
                    required=False)

parser.add_argument("-n", "--name",
                    action="store",
                    help="Custom name for a snapshot.\
                         If argument is not provided, defaults to 'Regular Snapshot DATE'",
                    metavar="\"CUSTOM_NAME\"",
                    type=str,
                    default="Regular Snapshot",
                    required=False)

parser.add_argument("-d", "--description",
                    action="store",
                    help="Custom description for a snapshot.\
                         If argument is not provided, defaults to \
                         'Regular Snapshot taken on DATE via virtualbox-snapshotter'",
                    metavar="\"CUSTOM_DESCRIPTION\"",
                    type=str,
                    default="Regular Snapshot taken on",
                    required=False)
args = parser.parse_args()


def delete_oldest_snapshots(machine_name: str, number_to_retain: int) -> None:
    """
    Attempts to delete oldest snapshots from specified machine.

    :param str machine_name: machine name to search for
    :param int number_to_retain: number of newest snapshots to retain
    :return: None
    """
    try:
        # Trying to find a machine
        virtual_machine = vbox.find_machine(machine_name)

        # Snapshot ids[0] and names[1] sorted from oldest (index - 0) to newest (index - highest)
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

        logger.info("Overall list of snapshot:")
        for snapshot in snapshot_details:
            logger.info("Snapshot ID: %s Name: %s", snapshot[0], snapshot[1])

        if number_to_retain > len(snapshot_details):
            logger.warning("Number of snapshots to be retained is bigger then number of available snapshots. "
                           "Snapshot deletion aborted.")
            return

        # Removing number of snapshots from the list of snapshots to be deleted
        snapshot_details = snapshot_details[:len(snapshot_details) - number_to_retain]

        logger.info("List of snapshots to be deleted:")

        if len(snapshot_details) == 0:
            # In case all existing snapshots to be retained
            logger.info("None")
            return

        for snapshot in snapshot_details:
            logger.info("Snapshot ID: %s, Name: %s", snapshot[0], snapshot[1])

        # Locking VM
        virtual_machine.lock_machine(session, virtualbox.library.LockType(1))
        for snapshot in snapshot_details:
            # Deleting snapshot by using Snapshot ID
            process = session.machine.delete_snapshot(snapshot[0])
            logger.info("Deleting snapshot: '%s'...", snapshot[1])
            process.wait_for_completion(timeout=-1)
            logger.info("Deleted snapshot: '%s'", {snapshot[1]})
    except Exception:
        logger.error("Snapshot deletion aborted prematurely:", stack_info=True, exc_info=True)


def create_snapshot(machine_name: str) -> bool:
    """
    Attempts to create a snapshot for a specified machine.

    :param str machine_name: machine name to search for
    :return: status of a machine if it was in any state but "Powered Off" initially
    :rtype: bool
    """
    # Assuming that machine is initially in any state but not in "Powered Off"
    vm_running_initially = True

    virtual_machine = vbox.find_machine(machine_name)
    if virtual_machine.state == virtualbox.library.MachineState(1):
        # Check if machine is powered off (MachineState(1) = PowerOff)
        vm_running_initially = False

        if session.state == virtualbox.library.SessionState(2):
            # Check if session is locked (SessionState(2) = Locked)
            session.unlock_machine()

        # Locks virtual machine from writes
        proc = virtual_machine.launch_vm_process(session, "headless", [])
        proc.wait_for_completion(timeout=-1)

    # Creating snapshot name and description
    snap_name = f"{args.name} {datetime.now().strftime('%d-%m-%Y')}"
    description = f"{args.description} {datetime.now().strftime('%d-%m-%Y')} via virtualbox-snapshotter"

    if vm_running_initially:
        # Check if initial state of a machine was anything but "Powered Off"
        if virtual_machine.session_state == virtualbox.library.SessionState(2):
            # Check if VM session is locked (SessionState(2) = Locked)
            if session.state == virtualbox.library.SessionState(2):
                # Check if current session is locked (SessionState(2) = Locked)
                session.unlock_machine()

        # Locking machine to allow making changes
        shared_lock_type = virtualbox.library.LockType(1)
        virtual_machine.lock_machine(session, shared_lock_type)

    logger.info("Creating snapshot: '%s'...", snap_name)
    # Taking snapshot
    process, _ = session.machine.take_snapshot(snap_name, description, False)
    process.wait_for_completion(timeout=-1)

    logger.info("Created snapshot: '%s'", snap_name)

    if vm_running_initially:
        # Check if initial state of a machine was anything but "Powered Off"
        if session.state == virtualbox.library.SessionState(2):
            # Check if session is locked
            session.unlock_machine()

    return vm_running_initially


def main():
    """
    Main code of virtualbox_snapshotter.

    1. Tries to delete old snapshots
    2. Tries to create a new snapshot
    """
    logger.info("Starting autosnapshotter script ...")

    delete_oldest_snapshots(args.machine_name, args.retain)
    vm_status = create_snapshot(args.machine_name)

    try:
        if not vm_status:
            session.console.power_down()
    except Exception:
        logger.error("Power down of virtual machine execution exited prematurely:", stack_info=True, exc_info=True)
        return


if __name__ == "__main__":
    # Setting up a global logger
    logger = logging.getLogger(__name__)

    # Setting up default logging string format
    logging.basicConfig(format="%(filename)s:%(levelname)s:%(asctime)s:%(funcName)s(): %(message)s",
                        datefmt="%d/%m/%Y %H:%M:%S")

    # Default log level is WARNING
    logger.setLevel(logging.WARNING)

    if args.verbose:
        # When verbosity flag is set, log level is changed to INFO
        logger.setLevel(logging.INFO)
    main()
