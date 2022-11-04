# stdlib Imports
import logging
import os
import re

# Zenoss Imports
from Products.ZenUtils.Utils import prepId
from Products.DataCollector.plugins.CollectorPlugin import PythonPlugin
from Products.DataCollector.plugins.DataMaps import ObjectMap, RelationshipMap
# Twisted Imports
from twisted.internet.defer import inlineCallbacks, returnValue

log = logging.getLogger('zen.DockerPlugin')


class nfs(PythonPlugin):
    """docker containers modeler plugin."""

    requiredProperties = (
        'zCommandUsername',
        'zCommandPassword',
        'zCommandPort',
        'zCommandCommandTimeout',
        'zKeyPath',
    )

    deviceProperties = PythonPlugin.deviceProperties + requiredProperties

    clients = {}

    commands = {
        'version': 'docker -v',
        # 'containers': 'sudo docker ps --no-trunc',
    }

    @inlineCallbacks
    def collect(self, device, log):
        """Asynchronously collect data from device. Return a deferred."""
        log.info('Collecting docker containers for device {}'.format(device.id))

        if device.zCommandUsername == '':
            log.warn('zCommandUsername is empty.')
            returnValue(None)
        if device.zCommandPassword == '':
            log.warn('zCommandPassword is empty, trying key authentication using %s', device.zKeyPath)
        keyPath = os.path.expanduser(device.zKeyPath)
        if os.path.isfile(keyPath):
            log.info('SSH key found.')
        else:
            if device.zCommandPassword is None or device.zCommandPassword == '':
                returnValue(None)

        options = {'hostname': str(device.manageIp),
                   'port': device.zCommandPort,
                   'user': device.zCommandUsername,
                   'password': device.zCommandPassword,
                   'identities': [keyPath],
                   'buffersize': 32768,
                   }

        timeout = device.zCommandCommandTimeout
        if timeout:
            timeout = int(timeout)
        else:
            timeout = 15

        client = self.getClient(options)

        results = {}
        # The command is not required, but a simple check on docker presence.
        for item, cmd in self.commands.items():
            try:
                response = yield client.run(cmd, timeout=timeout)
                results[item] = response
            except Exception, e:
                log.error("{} {} docker modeler error: {}".format(device.id, self.name(), e))
        returnValue(results)
