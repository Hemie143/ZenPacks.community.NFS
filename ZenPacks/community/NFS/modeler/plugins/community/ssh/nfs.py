# stdlib Imports
import logging
import re

# Zenoss Imports
from Products.DataCollector.plugins.CollectorPlugin import CommandPlugin


log = logging.getLogger('zen.NFS')

class nfs(CommandPlugin):
    """docker containers modeler plugin."""
    maptype = 'FilesystemMap'
    command = 'df -PTk'
    compname = 'os'
    relname = 'fileSystemNFSs'
    modname = 'ZenPacks.community.NFS.FileSystemNFS'

    deviceProperties = CommandPlugin.deviceProperties + (
        'zNFSFileSystemIgnoreNames',
    )

    def process(self, device, results, log):
        """Process results. Return iterable of datamaps or None."""
        NFSFileSystemIgnoreNames = getattr(device, 'zNFSFileSystemIgnoreNames', None)
        rm = self.relMap()
        dflines = results.split('\n')
        for line in dflines:
            if line.startswith('Filesystem') or not line:
                continue
            spline = line.split()
            if len(spline) != 7:
                log.warn('df is reporting an entry that is not recognized: {}'.format(spline))
                continue
            storage_device, storage_type, _, _, _, _, storage_mount = spline

            if not storage_type.startswith('nfs'):
                continue

            if NFSFileSystemIgnoreNames and re.search(NFSFileSystemIgnoreNames, storage_mount):
                log.info("{}: skipping {} (zNFSFileSystemIgnoreNames)".format(device.id, storage_mount))
                continue

            om = self.objectMap()
            om.id = self.prepId('nfs{}'.format(storage_mount))  # The first slash will be replaced by an underscore
            om.title = storage_mount
            om.storageDevice = storage_device
            om.type = storage_type
            om.mount = storage_mount
            rm.append(om)

        return [rm]
