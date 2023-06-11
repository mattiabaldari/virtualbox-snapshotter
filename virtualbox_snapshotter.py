"""
MIT License.

Copyright (c) 2020 Mattia Baldari

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from datetime import datetime
import argparse
import logging
import sys

import virtualbox


def delete_oldest_snapshots(machine_name: str, number_to_retain: int) -> None:
    """
    Attempts to delete oldest snapshots from specified machine.

    :param str machine_name: machine name to search for
    :param int number_to_retain: number of newest snapshots to retain
    :return: None
    """

    virtual_machine, snapshot_details = load_vm_and_snapshot_details(machine_name)
    if not snapshot_details:
        return

    logger.info("Overall list of snapshot:")

    for snapshot in snapshot_details:
        logger.info("Snapshot ID: %s Name: %s", snapshot[0], snapshot[1])

    if args.ignore is not None:
        # An ignore file is specified

        # Parsing snapshot ignore file
        uuids_to_retain = parse_snapshot_ignore_file(args.ignore)

        # Removing snapshot records if there are any matching records between
        # read from ignore file and available snapshots
        # TODO: This may potentially be slow when being run with thousands of records
        snapshot_details = [snapshot for snapshot in snapshot_details if snapshot[0] not in uuids_to_retain]

    if number_to_retain > len(snapshot_details):
        logger.warning("Number of snapshots to be retained is bigger then number of available snapshots. "
                       "Snapshot deletion aborted. Snapshot creation will proceed.")
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

    try:
        # Locking VM
        virtual_machine.lock_machine(session, virtualbox.library.LockType(1))
        for snapshot in snapshot_details:
            # Deleting snapshot by using Snapshot ID
            process = session.machine.delete_snapshot(snapshot[0])
            logger.info("Deleting snapshot: '%s'...", snapshot[1])
            process.wait_for_completion(timeout=-1)
            logger.info("Deleted snapshot: '%s'", snapshot[1])
    except virtualbox.lib.VBoxError:
        # Exiting application on exception as it may be due to user error (i.e. typo in machine name)
        # Snapshot deletion must not happen in such a case.
        logger.error("Snapshot deletion aborted prematurely", exc_info=True)
        sys.exit()


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


def parse_snapshot_ignore_file(filename: str) -> list:
    """
    Reads a list of VirtualBox snapshot UUIDs from a file.

    On OSError, returns an empty list.

    :param str filename: filename to read a list of VirtualBox snapshot UUIDs from
    :return: read list of VirtualBox snapshot UUIDs
    :rtype: list
    """
    uuids = []

    try:
        with open(file=filename, mode="rt", encoding="utf8") as file_stream:
            for dirty_line in file_stream:
                # String processing required as line may contain:
                # 1. Comments (those, starting with #)
                # 2. Whitespaces

                # Removing comments (starting with #) from read line
                comment_start_position = dirty_line.find("#")
                no_comment_line = dirty_line[:comment_start_position]

                # Removing whitespaces from processed line
                clean_line = no_comment_line.strip()
                uuids.append(clean_line)

    except OSError:
        logger.error("Exception while trying to read snapshot UUID ignore file",
                     exc_info=True)
        # Exiting application on exception as it may be due to user error (i.e. typo in ignore filename)
        # Snapshot deletion must not happen in such a case.
        sys.exit()

    return uuids


def load_vm_and_snapshot_details(machine_name: str) -> tuple[virtualbox.library.IMachine, list]:
    """
    Loads virtual machine object and virtual machine snapshots' details.

    :param str machine_name: name of a virtual machine
    :return: virtual machine object and all snapshot details
    :rtype: tuple
    """

    virtual_machine = virtualbox.library.IMachine()
    snapshot_details = []
    try:
        # Trying to find a machine
        virtual_machine = vbox.find_machine(machine_name)

        # Snapshot ids[0], names[1], descriptions[2] are sorted from oldest (index 0) to newest
        snapshot_details = []
        # Getting root snapshot and adding it to a list
        try:
            snapshot = virtual_machine.find_snapshot("")
        except Exception as err:
            if err.value == 2147614729 and "This machine does not have any snapshots" in err.msg:
                return virtual_machine, None

        snapshot_details.append([snapshot.id_p, snapshot.name, snapshot.description])

        # Traversing through children snapshots (until one has no children) and adding them to a list
        while snapshot.children_count != 0:
            # TODO: Implement multi children scan
            # This check skips snapshot marked as "Current State"
            snapshot = snapshot.children[0]
            snapshot_details.append([snapshot.id_p, snapshot.name, snapshot.description])
    except virtualbox.lib.VBoxError:
        # 1. Could not find a registered machine named `machine_name`
        # 2. Machine does not have any snapshots
        logger.error("Could not find a registered machine named '%s' or "
                     "machine does not have any snapshots", machine_name, exc_info=True)
        sys.exit()

    return virtual_machine, snapshot_details


def main():
    """
    Main code of virtualbox_snapshotter.

    1. Tries to delete old snapshots
    2. Tries to create a new snapshot
    """
    logger.info("Starting autosnapshotter script ...")

    if args.list:
        _, snapshot_details = load_vm_and_snapshot_details(args.machine_name)
        # Avoiding to use logger here to not clutter output which may be of some use for user
        print(f"Available snapshots for '{args.machine_name}':")
        if not snapshot_details:
            print(f"0 snapshots")
        else:
            for snapshot in snapshot_details:
                print(f"Name: '{snapshot[1]}' UUID: {snapshot[0]}")
                print(f"\tDescription: {snapshot[2]}")
            return


    delete_oldest_snapshots(args.machine_name, args.retain)
    vm_status = create_snapshot(args.machine_name)

    try:
        if not vm_status:
            session.console.power_down()
    except virtualbox.lib.VBoxError:
        # Virtual machine must be Running, Paused or Stuck to be powered down.
        logger.error("Power down of virtual machine execution exited prematurely", exc_info=True)
        return


if __name__ == "__main__":
    # Setting up a global logger
    logger = logging.getLogger(__name__)

    # Setting up default logging string format
    logging.basicConfig(format="%(filename)s:%(levelname)s:%(asctime)s:%(funcName)s: %(message)s",
                        datefmt="%d/%m/%Y %H:%M:%S")

    # Default log level is WARNING
    logger.setLevel(logging.WARNING)

    # Global placeholders
    vbox = virtualbox.VirtualBox()
    session = virtualbox.Session()

    # Adding argparse to application
    parser = argparse.ArgumentParser(prog="VirtualBox Snapshotter",
                                     description="Takes new snapshots and deletes old ones "
                                                 "for specified Virtual Machine.",
                                     epilog="Currently, multi children are not supported. "
                                            "Nested children are supported.")

    # Adding arguments to argparse
    parser.add_argument("machine_name",
                        action="store",
                        help="(Required) Virtual Machine (VM) name enclosed in double quotes (\"). "
                             "Not using double quotes may lead to abnormal behaviour if name contains whitespaces.",
                        metavar="\"VIRTUAL_MACHINE_NAME\"",
                        type=str)

    parser.add_argument("-r", "--retain",
                        action="store",
                        choices=range(0, 1000),
                        default=3,
                        help="Number of latest snapshots to retain. "
                             "When used with '-i'/'--ignore', counts only those snapshots, that are NOT ignored. "
                             "I.e. 2 snapshot are ignored via '-i'/'--ignore', 3 snapshots specified for "
                             "'-r'/'--retain', resulting number of preserved snapshots will be 5. "
                             "If 0 is provided - deletes all snapshots leaving just the latest one. "
                             "If argument is not provided, defaults to 3.",
                        metavar="(0-1000)",
                        type=int,
                        required=False)

    parser.add_argument("-v", "--verbose",
                        action="store_true",
                        help="Adds verbosity",
                        required=False)

    parser.add_argument("-n", "--name",
                        action="store",
                        help="Custom name for a snapshot. "
                             "If argument is not provided, defaults to 'Regular Snapshot CURRENT_DATE'",
                        metavar="\"CUSTOM_SNAPSHOT_NAME\"",
                        type=str,
                        default="Regular Snapshot",
                        required=False)

    parser.add_argument("-d", "--description",
                        action="store",
                        help="Custom description for a snapshot. "
                             "If argument is not provided, defaults to "
                             "'Regular Snapshot taken on CURRENT_DATE via virtualbox-snapshotter'",
                        metavar="\"CUSTOM_SNAPSHOT_DESCRIPTION\"",
                        type=str,
                        default="Regular Snapshot taken on",
                        required=False)

    parser.add_argument("-i", "--ignore",
                        action="store",
                        help="Path to a file, containing snapshot IDs to be ignored from deletion. "
                             "Snapshot UUIDs specified within a file will never be deleted.",
                        metavar="\"SNAPSHOT_IGNORE_FILENAME\"",
                        type=str,
                        required=False
                        )

    parser.add_argument("-l", "--list",
                        action="store_true",
                        help="Lists all snapshots and their details (name, UUID, date) for selected virtual machine. "
                             "When '-l'/'--list' is specified, no actions (i.e. snapshot delete, machine lock etc) "
                             "are performed on a virtual machine apart from reading virtual machine's details. "
                             "When '-l'/'--list' argument is used, any other optional argument has no effect",
                        required=False
                        )

    # Parsing arguments
    args = parser.parse_args()

    if args.verbose:
        # When verbosity flag is set, log level is changed to INFO
        logger.setLevel(logging.INFO)

    main()
