# Contributing guide

## Welcome

Welcome to contributing guide! Thank you for checking out this guide and considering implementing changes. Any changes - small or big - are always welcomed and appreciated!

## Start contributing

- Fork current repository
- [Install the VirtualBox SDK](supplementary-materials/virtualbox-sdk/README.md)
- In forked repo, branch out of `master`
- [Create a Python virtual environment](https://docs.python.org/3/library/venv.html#creating-virtual-environments)
- Enable Python virtual environment
- Install required modules from `requirements_dev.txt`: this will install linting tools (`prospector`, linting rules are preconfigured already and are available at `.prospector.yaml`) along the rest required modules for the code
- Implement changes
- Test implemented changes
- Ensure linting is succeeding via `prospector`:

```bash
prospector              # Lint all files
prospector FILE_NAME    # Lint a single file called FILE_NAME
```

- After all linting checks pass with no errors, push all the changes to forked repository branch
- Create a Pull Request from forked repository to original repository `master` branch
- Grab yourself a cup of tea/coffee and await Pull Request review
  - Possible improvements/further changes will be discussed during Pull Request review
  - After successful Pull Request review, branch will be merged
- (Optional) Delete branch from forked repo (on a remote and locally)
- Within forked repo, checkout and pull `master` branch to be in sync with original repo `master` branch

Again, thank you so much for your contribution!
