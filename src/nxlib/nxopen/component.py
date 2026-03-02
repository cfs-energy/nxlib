# Copyright 2026 Commonwealth Fusion Systems (CFS), all rights reserved.
# This entire source code file represents the sole intellectual property of CFS.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import NXOpen  # pyright: ignore[reportMissingModuleSource]
import NXOpen.Assemblies  # pyright: ignore[reportMissingModuleSource]


def component_is_reference(component: NXOpen.Assemblies.Component) -> bool:
    """
    Determine whether a component is 'Reference-Only'.

    A component is reference only if it has the attribute called REFERENCE_COMPONENT.
    """
    try:
        # This will return an empty string if it exists.
        _isref = component.GetInstanceStringUserAttribute("REFERENCE_COMPONENT", -1)
    except NXOpen.NXException as err:
        # If the attribute wasn't found, it will say so in the error message.
        # If the error message does not indicate a missing attribute, something
        # else is wrong and we need to raise it
        if "The attribute not found." not in err.args[0]:
            raise
        # If the component does not have the REFERENCE_COMPONENT attribute then
        # it is not reference only.
        return False
    return True
