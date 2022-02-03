"""
Plotlyst
Copyright (C) 2021-2022  Zsolt Kovari

This file is part of Plotlyst.

Plotlyst is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Plotlyst is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from fbs_runtime.application_context.PyQt5 import ApplicationContext


class ResourceRegistry:

    def __init__(self):
        self._cork = None
        self._frame1 = None
        self._cover1 = None
        self._banner = None

    def set_up(self, app_context: ApplicationContext):
        self._cork = app_context.get_resource('cork.wav')
        self._frame1 = app_context.get_resource('frame_1.png')
        self._cover1 = app_context.get_resource('cover_1.jpg')
        self._banner = app_context.get_resource('plotlyst_banner.jpg')

    @property
    def cork(self):
        return self._cork

    @property
    def frame1(self):
        return self._frame1

    @property
    def cover1(self):
        return self._cover1

    @property
    def banner(self):
        return self._banner


resource_registry = ResourceRegistry()
