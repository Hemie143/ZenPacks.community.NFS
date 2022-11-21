import logging
import re

from Products.ZenRRD.CommandParser import CommandParser
from Products.ZenEvents import ZenEventClasses

log = logging.getLogger("zen.command.parsers.nfs.catfile")


class catfile(CommandParser):

    createDefaultEventUsingExitCode = False

    def dataForParser(self, context, dp):
        return {
            'mount': getattr(context, 'mount', ''),
            'zNFSMountFilename': getattr(context, 'zNFSMountFilename', ''),
            'zNFSMountFileContent': getattr(context, 'zNFSMountFileContent', ''),
        }

    def processResults(self, cmd, result):
        for dp in cmd.points:
            mount = dp.data['mount']
            NFSMountFilename = dp.data['zNFSMountFilename']
            NFSMountFileContent = dp.data['zNFSMountFileContent']
            if not NFSMountFilename:
                NFSMountFilename = 'zenoss_placeholder.txt'
            if not NFSMountFileContent:
                NFSMountFilename = 'hello'
            if cmd.result.exitCode > 0:
                # If the placeholder file is not found, it should be captured by another event
                result.values.append((dp, ZenEventClasses.Error))
                result.events.append(dict(
                    severity=ZenEventClasses.Clear,
                    summary='Placeholder file is not checked'.format(mount),
                    eventClassKey='nfs_filecontent',
                    eventKey='nfs_filecontent',
                    eventClass='/Status/Filesystem/NFS',
                    component=cmd.component,
                ))
            else:
                if dp.id == 'filecontent':
                    for line in cmd.result.output.splitlines():
                        r = re.match(NFSMountFileContent, line)
                        if r:
                            result.values.append((dp, ZenEventClasses.Clear))
                            result.events.append(dict(
                                severity=ZenEventClasses.Clear,
                                summary='Placeholder file is verified'.format(mount),
                                eventClassKey='nfs_filecontent',
                                eventKey='nfs_filecontent',
                                eventClass='/Status/Filesystem/NFS',
                                component=cmd.component,
                            ))
                            break
                    else:
                        result.values.append((dp, ZenEventClasses.Error))
                        result.events.append(dict(
                            severity=ZenEventClasses.Error,
                            summary="Placeholder file's content {}/{} does not match {}".format(mount, NFSMountFilename,
                                                                                                NFSMountFileContent),
                            eventClassKey='nfs_filecontent',
                            eventKey='nfs_filecontent',
                            eventClass='/Status/Filesystem/NFS',
                            component=cmd.component,
                        ))

        log.debug('catfile result: {}'.format(result))