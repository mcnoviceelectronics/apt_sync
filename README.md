# apt_sync
Use to copy (scp) Raspberry Pi cached apt archives to a Linux Server.  Not tested on any other systems

See article on my website: [Raspberry Pi - Creating Local Apt Repository](https://mcnoviceelectronics.wordpress.com/2018/03/22/raspberry-pi-creating-local-apt-repository/)

## Usage
```bash
./apt_sync.py
```

* The first time the program is run it will create a config file *~/.apt_sync/apt_sync.ini*, which needs to be edited by the user
* The second run will copy the entire apt archive to the server.  You will need to enter server password for copy to work.
* Subseqent runs will only copy the files that were added since last run

## Config File - apt_sync.ini
```ini
[APT_SYNC]
LogLevel = INFO
SCPHost = 192.168.1.100
SCPUser = user
SCPLocation = /opt/apt-mirror/raspbian/stretch
APTArchives = /var/cache/apt/archives

[APT_DATA]
LastModified = 
```
* Valid values for *LogLevel* are *DEBUG, INFO, WARN, ERROR*
* *SCPHost* is the host IP for the secure copy
* *SCPUser* is the username for the secure copy
* *SCPLocation* is the server destination location for secure copy 
* *APTArchives* is the local machine location for the apt archives
* *LastModified* is used by the program to write the *APTArchives* directory last modified time, in EPOCH format
