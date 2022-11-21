Goal
----
Monitor NFS Filesystem. The ZenPack models the available NFS filesystems on the device, checks whether they are available, checks for a placeholder file and for its content.

Protocol
--------
SSH

Commands used: 
 - df -PTk
 - ls
 - cat

Releases
--------

 - 1.0.0 (21/11/2022) : First release

Next features / Bugs
--------------------
nihil

Metrics
-------
nihil

zProperties
-----------
| Name  |  Type | Default  |  Comments |
|---|---|---|---|
|  zNFSFileSystemIgnoreNames | string  |   | NFS Filesystem names to ignore (regular expression)  |
| zNFSMountFilename  |  string | zenoss_placeholder.txt  |Filename to check   |
| zNFSMountFileContent  | string  | hello  |  Content to check within placeholder file |

Templates
---------
| Name  | Device Class  |
|---|---|
| FileSystemNFS  | /Server/SSH/Linux  |

Event Classes
-------------
| Event Class  | Transform | Mappings |
|---|----|----------|
|  /Status/Filesystem/NFS | N | N |
