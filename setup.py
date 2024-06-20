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

from setuptools import setup, find_packages
from pi_control_hub_driver_ir import __author__, __author_email__, __version__


setup(
    name='pi_control_hub_driver_ir',
    version=__version__,
    description='PiControl Hub driver to control devices using IR.',
    url='https://github.com/PiControl/pi_control_hub_driver_ir',
    author=__author__,
    author_email=__author_email__,
    license='Apache 2.0',
    packages=find_packages(),
    package_data={
        "pi_control_hub_driver_ir.icons": ["*.png"]
    },
    install_requires=[
        'pi_control_hub_driver_api @ git+https://github.com/PiControl/pi_control_hub_driver_api.git@main#egg=pi_control_hub_driver_api',
        'PiIR>=0.2.5'
    ],
    entry_points={
        "pi_control_hub_driver": [
            "driver_descriptor = pi_control_hub_driver_ir.device_driver:get_driver_descriptor"
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3',
    ],
)
