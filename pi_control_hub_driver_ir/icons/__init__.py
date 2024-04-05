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

import os
import pathlib


__directory = pathlib.Path(__file__).parent.resolve()
__image_data = {}

def __read_icon(filename: str) -> bytes:
    filepath = os.path.join(__directory, filename)
    if filepath in __image_data:
        return __image_data[filepath]

    with open(filepath, mode="rb") as f:
        data: bytes = f.read()
        __image_data[filepath] = data
        return data

def unknown() -> bytes: return __read_icon("unknown.png")

def read_icon_for_key(key: str) -> bytes:
    filepath = os.path.join(__directory, key) + ".png"
    if not pathlib.Path(filepath).is_file():
        return unknown()
    return __read_icon(key + ".png")
