import logging

from Products.ZenRRD.CommandParser import CommandParser
from Products.ZenEvents import ZenEventClasses

log = logging.getLogger("zen.command.parsers.nfs.fsls")


class fsls(CommandParser):

    createDefaultEventUsingExitCode = False

    def dataForParser(self, context, dp):
        return {
            'mount': getattr(context, 'mount', ''),
            'zNFSMountFilename': getattr(context, 'zNFSMountFilename', ''),
        }

    def processResults(self, cmd, result):
        for dp in cmd.points:
            NFSMountFilename = dp.data['zNFSMountFilename']
            if not NFSMountFilename:
                NFSMountFilename = 'zenoss_placeholder.txt'
            mount = dp.data['mount']
            if cmd.result.exitCode > 0:
                # Folder and file status
                result.values.append((dp, ZenEventClasses.Error))           # Could not access the filesystem
                if dp.id == 'fsstatus':
                    result.events.append(dict(
                        severity=ZenEventClasses.Error,
                        summary='NFS Filesystem {} is not reachable'.format(mount),
                        eventClassKey='nfs_fsstatus',
                        eventKey='nfs_fsstatus',
                        eventClass='/Status/Filesystem/NFS',
                        component=cmd.component,
                    ))
                elif dp.id == 'filestatus':
                    result.events.append(dict(
                        severity=ZenEventClasses.Clear,                     # Do not create an additional event
                        summary='Placeholder file is not checked',
                        eventClassKey='nfs_filestatus',
                        eventKey='nfs_filestatus',
                        eventClass='/Status/Filesystem/NFS',
                        component=cmd.component,
                    ))
            else:
                if dp.id == 'fsstatus':
                    result.values.append((dp, ZenEventClasses.Clear))       # Filesystem is available
                    result.events.append(dict(
                        severity=ZenEventClasses.Clear,
                        summary='NFS Filesystem {} is reachable'.format(mount),
                        eventClassKey='nfs_fsstatus',
                        eventKey='nfs_fsstatus',
                        eventClass='/Status/Filesystem/NFS',
                        component=cmd.component,
                    ))
                elif dp.id == 'filestatus':
                    for line in cmd.result.output.splitlines():
                        if len(line.split()) != 9:
                            continue
                        else:
                            filename = line.split()[8]
                            if filename == NFSMountFilename:
                                result.values.append((dp, ZenEventClasses.Clear))
                                result.events.append(dict(
                                    severity=ZenEventClasses.Clear,
                                    summary='Placeholder file {}/{} is found'.format(mount, NFSMountFilename),
                                    eventClassKey='nfs_filestatus',
                                    eventKey='nfs_filestatus',
                                    eventClass='/Status/Filesystem/NFS',
                                    component=cmd.component,
                                ))
                    else:
                        result.values.append((dp, ZenEventClasses.Error))
                        result.events.append(dict(
                            severity=ZenEventClasses.Error,
                            summary='Placeholder file {}/{} is not found'.format(mount, NFSMountFilename),
                            eventClassKey='nfs_filestatus',
                            eventKey='nfs_filestatus',
                            eventClass='/Status/Filesystem/NFS',
                            component=cmd.component,
                        ))

        log.debug('fsls result: {}'.format(result))
