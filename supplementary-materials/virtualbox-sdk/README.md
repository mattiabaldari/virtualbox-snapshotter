# VirtualBox SDK

## VirtualBox 6.0.x support

By the looks of it, VirtualBox 6.0.x is no longer supported as per official website:
![VirtualBox-6.0.x-is-no-longer-supported](../images/no_longer_supported.png?raw=true)

## VirtualBox SDK installation

1. Go to VirtualBox’s [download page](<https://www.virtualbox.org/wiki/Downloads>) and download `VirtualBox X.Y.Z Software Developer Kit (SDK)`:
![VirtualBox-SDK](../images/VirtualBox-SDK.png?raw=true)
2. Extract the contents of an archive
3. Open a terminal (CMD, bash, etc.)
4. Within terminal, navigate where `vboxapisetup.py` is located. It should be located in `sdk/installer`
![cmd-path](../images/cmd.png?raw=true)

5. From within the installer folder run the following command:

```bash
python vboxapisetup.py install 
```

__NOTE__ Sometimes, `vboxapisetup.py` fails to install first time - it creates caches and fails to read them. In such a case, try running the command above once more and it may fix the issue.
