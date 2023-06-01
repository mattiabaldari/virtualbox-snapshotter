# VirtualBox Snapshotter

![shield-license](https://img.shields.io/github/license/Meru3m/virtualbox-snapshotter)
![shield-code-size](https://img.shields.io/github/languages/code-size/Meru3m/virtualbox-snapshotter)
![shield-issues](https://img.shields.io/github/issues/Meru3m/virtualbox-snapshotter)

## Contributing

Guide on how to contribute to this repository is described within [CONTRIBUTING.md](CONTRIBUTING.md)

## Description

Python script to automate Virtualbox snapshotting process. It uses circular logic aka "oldest snapshot out, newest snapshot in" with an ability to customise total amount of snapshots to retain. Moreover, it provides and ability to customise snapshot details.

## Dependency

In order to function, this script relies on [VirtualBox SDK](https://www.virtualbox.org/wiki/Downloads)

## Installation process

__WARNING__ This guide shows how to install modules, required by this script, into ROOT of the Python. Usually, this is not a best practice as it may cause module conflicts in a long run. Please use Python [virtual environment (venv)](<https://docs.python.org/3/library/venv.html>) for a best practice. To avoid making this readme enormous, its up to a user to sort out the virtual environment for Python.

Installation guide on Youtube: <https://www.youtube.com/watch?v=uDEFQyu4MvM>

### Installation

1. [Install the VirtualBox SDK](supplementary-materials/virtualbox-sdk/README.md)
2. Download the project as a `zip` archive
3. Unzip downloaded `zip` archive
4. Open a terminal (CMD, bash, etc.)
5. Within terminal, navigate into the project directory
6. Install the requirements file and wait for it to complete:

```bash
python -m pip install -r requirements.txt
```

__Note__ Remember to run the installation command from within the project directory:
![requirements-install-info](supplementary-materials/images/requirements.png?raw=true)

## Usage

```bash
usage: VirtualBox Snapshotter [-h] [-r 0-1000] [-v] [-n "CUSTOM_SNAPSHOT_NAME"] [-d "CUSTOM_SNAPSHOT_DESCRIPTION"] [-i "SNAPSHOT_IGNORE_FILENAME"] [-l] "VIRTUAL_MACHINE_NAME"
```

### Positional parameter

__NOTE__ Without specifying this parameter, script will fail to run.

- `"VIRTUAL_MACHINE_NAME"` - Virtual Machine (VM) name enclosed in double quotes ("). Not using double quotes may lead to abnormal behaviour if name contains whitespaces.

### Optional parameters

- `-h` or `--help` - displays a help message
- `-v` or `--verbose` - script will become more verbose (will produce more textual output). Useful for debugging.
- `-r NUMBER` or `--retain NUMBER` - Number of latest snapshots to retain. Replace `NUMBER` with a number between 0 (incl.) and 1000 (incl.). When used with `-i`/`--ignore`, counts only those snapshots, that are NOT ignored. I.e. 2 snapshot are ignored via `-i`/`--ignore`, 3 snapshots specified for `-r`/`--retain`, resulting number of preserved snapshots will be 5. If 0 is provided - deletes all snapshots leaving just the latest one. If argument is not provided, defaults to 3.
- `-n "CUSTOM_SNAPSHOT_NAME"` or `--name "CUSTOM_SNAPSHOT_NAME"` - Customise name for a snapshot. Replace `CUSTOM_SNAPSHOT_NAME` to any text for a custom snapshot name. Make sure to enclose your custom snapshot name within double quotes ("). If argument is not provided, defaults to `Regular Snapshot CURRENT_DATE`
- `-d "CUSTOM_SNAPSHOT_DESCRIPTION"` or `--description "CUSTOM_SNAPSHOT_DESCRIPTION"` - Customise description for a snapshot. Replace `CUSTOM_SNAPSHOT_DESCRIPTION` to any text for a custom snapshot description. Make sure to enclose your custom snapshot description within double quotes ("). If argument is not provided, defaults to `Regular Snapshot taken on CURRENT_DATE via virtualbox-snapshotter`
- `-i SNAPSHOT_IGNORE_FILENAME` or `--ignore SNAPSHOT_IGNORE_FILENAME` - Path to a file, containing snapshot UUIDs to be ignored from deletion. Snapshot UUIDs specified within a file will never be deleted. Snapshot UUIDs can be found via [VBoxManage](https://www.virtualbox.org/manual/ch08.html#vboxmanage-snapshot) or via this script, using `-l`/`--list` argument. `SNAPSHOT_IGNORE` file supports comments - any text after `#` will be ignored. Moreover, any whitespace within a file is ignored. Example structure of `SNAPSHOT_IGNORE` file:

```text
5ead9089-84f2-4883-969a-0eae3cda0813    # this is very cool snapshot ID which will never be deleted
aeeff25-62b1-ffa5-521f-e26a3cda11ab     # this is another very cool snapshot ID which will never be deleted
```

- `-l` or `--list` - Lists all snapshots and their details (name, UUID, date) for selected virtual machine. When `-l`/`--list` is specified, no actions (i.e. snapshot delete, machine lock etc) are performed on a virtual machine apart from reading virtual machine's details. When `-l`/`--list` argument is used, any other optional argument has no effect.

### Optional parameter defaults

- No verbosity
- Snapshot retain amount: `3`
- Snapshot name: `Regular Snapshot CURRENT_DATE`
- Snapshot description: `Regular Snapshot taken on CURRENT_DATE via virtualbox-snapshotter`

### Example usage

This will run with default optional parameters:

```bash
python virtualbox_snapshotter.py "My awesome VM"
```

---

This will retain 5 snapshots, other optional parameters will use default values:

```bash
python virtualbox_snapshotter.py "My awesome VM" -r 5
```

---

This will retain 0 snapshots, will write a custom snapshot name and other optional parameters will use default values:

```bash
python virtualbox_snapshotter.py "My awesome VM" -r 0 -n "My awesome snapshot name"
```

---

This will retain 10 snapshots, will write a custom snapshot name and snapshot description. Other optional parameters will use default values:

```bash
python virtualbox_snapshotter.py "My awesome VM" -r 10 -n "My awesome snapshot name" -d "My awesome snapshot description"
```

---

This will retain 15 snapshots (potentially - more, depending on `ignore.txt` content), will write a custom snapshot name and snapshot description, ignore deleting specific snapshots as specified in `ignore.txt`. Other optional parameters will use default values:

```bash
python virtualbox_snapshotter.py "My awesome VM" -r 15 -n "My awesome snapshot name" -d "My awesome snapshot description" -i "ignore.txt"
```

---

This will list all snapshots (if any) and their details (name, UUID, date) for selected virtual machine:

```bash
python virtualbox_snapshotter.py "My awesome VM" -l
```

## Scheduling

The script itself does not provide an ability to schedule when it should be run. However, most mainstream operating systems provide an ability to schedule tasks:

- [[Win-10] Task scheduler](<https://www.windowscentral.com/how-create-automated-task-using-task-scheduler-windows-10>)

- [[Win-11] Task scheduler](<https://www.windowscentral.com/how-create-automated-tasks-windows-11>)

- [[Linux] Crontab](<https://askubuntu.com/questions/2368/how-do-i-set-up-a-cron-job>)

## FAQ

__Q:__ When the script is run with X snapshots to retain, the end result is X+1 amount of snapshots. Is this correct?

__A:__ Yes, this is correct. If X amount of snapshots to retain is specified, the script will retain X amount of snapshots. However, a new snapshot will be taken after X amount of snapshots retained, meaning that total amount of snapshots will be X+1, where X - total amount of snapshots to retain. Example: retain amount - 5. All but 5 snapshots are deleted. Then, a new snapshot is taken. End result - 6 snapshots.

---

__Q:__ Script takes forever to run. It even seems like it does not do anything. Am I in trouble?

__A:__ No, you are not in trouble. It relies on VirtualBox SDK which merges changes between snapshots. This means, the more snapshots you have and the more changes you have done to the Virtual Machine in between the snapshots, the longer it will take to run and merge the changes. Just be patient and eventually, it will finish its work. If you want to make sure it actually does things under the hood, make use of `-v` optional argument to check its progress.
