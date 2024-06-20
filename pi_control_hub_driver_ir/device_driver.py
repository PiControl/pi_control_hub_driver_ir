"""
   Copyright 2024 Thomas Bonk

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import json
import os
from typing import List, Tuple
from uuid import UUID, uuid4

import piir
from pi_control_hub_driver_api import (AuthenticationMethod, DeviceCommand,
                                       DeviceDriver, DeviceDriverDescriptor,
                                       DeviceInfo, DeviceNotFoundException,
                                       DeviceDriverException)

from pi_control_hub_driver_ir.icons import read_icon_for_key


class LircDeviceCommand(DeviceCommand):
    def __init__(self, cmd_id: int, title: str, key: str, device_id: str):
        DeviceCommand.__init__(self, cmd_id, title, read_icon_for_key(key))
        self._key = key
        self._device_id = device_id

    async def execute(self):
        """
        Execute the command. This method must be implemented by the specific command.

        Raises
        ------
        `DeviceCommandException` in case of an error while executing the command.
        """
        try:
            lirc_client = lirc.Client()
            lirc_client.send_once(self._device_id, self._key)
            lirc_client.close()
        except lirc.exceptions.LircdConnectionError:
            pass

class LircDeviceDriver(DeviceDriver):
    def __init__(self, device_info: DeviceInfo):
        DeviceDriver.__init__(self, device_info)
        try:
            remote_defition_path = os.path.join(
                DeviceDriverDescriptor.get_config_path(),
                "pi_control_hub_driver_ir"
            )
            filepath = os.path.join(remote_defition_path, device_info.device_id)
            with open(filepath, encoding="utf-8") as f:
                content: str = f.read()
                self._remote_definition = json.loads(content)
        except Exception as ex:
            raise DeviceDriverException("Error while reading the remote definition", ex) from ex

    async def get_commands(self) -> List[DeviceCommand]:
        """Return the commands that are supported by this device.

        Returns
        -------
        The commands that are supported by this device.

        Raises
        ------
        `DeviceDriverException` in case of an error.
        """
        keys = self._remote_definition["keys"]
        commands = []
        for i, key in enumerate(sorted(list(keys.keys()))):
            commands.append(LircDeviceCommand(i, key, key, self.device_id))
        return commands

    @property
    def remote_layout_size(self) -> Tuple[int, int]:
        """
        The size of the remote layout.

        Returns
        -------
        A tuple with the width and height of the layout
        """
        remote = self._remote_definition["remote"]
        return remote["width"], remote["height"]

    @property
    def remote_layout(self) -> List[List[int]]:
        """
        The layout of the remote.

        Returns
        -------
        The layout as a list of columns.
        """
        remote = self._remote_definition["remote"]
        layout = remote["layout"]
        return []

    async def execute(self, command: DeviceCommand):
        """
        Executes the given command.

        Parameters
        ----------
        command : DeviceCommand
            The command that shall be executed

        Raises
        ------
        `DeviceCommandException` in case of an error while executing the command.
        """
        await command.execute()

    @property
    async def is_device_ready(self) -> bool:
        """
        A flag the determines whether the device is ready.

        Returns
        -------
        true if the device is ready, otherwise false.
        """
        return self._lirc_client is not None


class LircDeviceDriverDescriptor(DeviceDriverDescriptor):
    def __init__(self):
        DeviceDriverDescriptor.__init__(
            self,
            UUID("ba7c5fce-f23f-11ee-a951-0242ac120002"),     # driver id
            "IR Controlled Devices",                          # display name
            "PiControl Hub driver for controling IR devices", # description
        )
        self._remote_defition_path = os.path.join(
            DeviceDriverDescriptor.get_config_path(),
            "pi_control_hub_driver_ir"
        )
        if not os.path.isdir(self._remote_defition_path):
            self._remote_defition_path = None

    async def get_devices(self) -> List[DeviceInfo]:
        """Returns a list with the available device instances."""
        if self._remote_defition_path is not None:
            remotes = [f for f in os.listdir(self._remote_defition_path)
                       if os.path.isfile(os.path.join(self._remote_defition_path, f)) and
                       (len(os.path.splitext(f)) > 1) and
                       os.path.splitext(f)[1] == ".remote"]
            return list(map(lambda f: DeviceInfo(os.path.splitext(f)[0], f), remotes))
        return []

    async def get_device(self, device_id: str) -> DeviceInfo:
        """Gets the device with the given ID"""
        devices = list(filter(lambda d: d.device_id == device_id, await self.get_devices()))
        if len(devices) == 0:
            raise DeviceNotFoundException(device_id=device_id)
        return devices[0]

    @property
    def authentication_method(self) -> AuthenticationMethod:
        """The authentication method that is required when pairing a device."""
        return AuthenticationMethod.NONE

    @property
    def requires_pairing(self) -> bool:
        """This flag determines whether pairing is required to communicate with this device."""
        return False

    async def start_pairing(self, device_info: DeviceInfo, remote_name: str) -> Tuple[str, bool]:
        """Start the pairing process with the given device.

        Parameters
        ----------
        device_info : DeviceInfo
            The device to pair with.
        remote_name : str
            The name of the remote that will control this device.

        Returns
        -------
        A tuple consisting of a pairing request ID and a flag that determines whether the device
        provides a PIN.
        """
        return str(uuid4()), False

    async def finalize_pairing(self, pairing_request: str, credentials: str, device_provides_pin: bool) -> bool:
        """Finalize the pairing process

        Parameters
        ----------
        pairing_request : str
            The pairing request ID returns by ``start_pairing``
        device_provides_pin : bool
            The flag that determines whether the device provides a PIN.
        """
        return True

    async def create_device_instance(self, device_id: str) -> DeviceDriver:
        """Create a device driver instance for the device with the given ID.

        Parameters
        ----------
        device_id : str
            The ID of the device.

        Returns
        -------
        The instance of the device driver or None in case of an error.
        """
        return LircDeviceDriver(await self.get_device(device_id))


def get_driver_descriptor() -> DeviceDriverDescriptor:
    return LircDeviceDriverDescriptor()
