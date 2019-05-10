Parrot Zik TCP Server
========

## Overview

Parrot Zik is one of the most advanced headphones in the market.
https://www.parrot.com/en/audio/parrot-zik-3

PyParrot Zik is unofficial tool that show Parrot Zik indicator on Windows and Linux.
Thanks to [@serathius](https://github.com/serathius) for Parrot Zik 2.0 support.
Thanks to [@moimadmax](https://github.com/moimadmax) for Parrot Zik 3.0 support.
Thanks to [@m0sia](https://github.com/m0sia/pyParrotZik) for base code and the
reverse engineering of Parrot Zik communication protocol.

This repo contains some base class without unmaintained pyGTK crap and python3
compatible code with a simple TCP client/server for use this.

/!\ Parrot Zik 1 not tested for the moment.

## Windows Usage

Windows support is not tested for the moment. All old code from forked project
is always here.

## Linux Usage

1. Connect Parrot Zik with standard bluetooth connection
2. Install the server
   ```
   python setup install
   ```
3. Run the server
   ```
   parrot_zik_tray
   ```

Battery status are save all 90 seconds in tmp file. You can use the simple
client to use the server or build your own TCP client.

### Linux Requirement

Python-bluez is needed. On ubuntu based distro run

```
sudo apt-get install python-bluez python-appindicator python-beautifulsoup
```

## Mac OS Usage

Based on investigation made for pyParrotZik the excellent Parrot-Status tool was developed specially for Mac OS (https://github.com/vincent-le-normand/Parrot-Status)
