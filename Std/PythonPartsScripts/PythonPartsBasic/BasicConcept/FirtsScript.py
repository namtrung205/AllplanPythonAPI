"""
Example script for AllControsl
"""

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements

from PythonPart import View2D3D, PythonPart

print('Load AllControls.py')


def check_allplan_version(build_ele, version):
    """
    Check the current Allplan version

    Args:
        build_ele: the building element.
        version:   the current Allplan version

    Returns:
        True/False if version is supported by this script
    """

    # Delete unused arguments
    del build_ele
    del version

    # Support all versions
    return True


def create_element(build_ele, doc):
    """
    Creation of element

    Args:
        build_ele: the building element.
        doc:       input document
    """
    element = AllControls(doc)

    return element.create(build_ele)


def modify_element_property(build_ele, name, value):
    """
    Modify property of element

    Args:
        build_ele:  the building element.
        name:       the name of the property.
        value:      new value for property.

    Returns:
        True/False if palette refresh is necessary
    """

    if name == "Length":
        build_ele.Area.value = value * value * 6
        build_ele.Volume.value = value * value * value

    return True

class AllControls():
    """
    Definition of class Visibility
    """

    def __init__(self, doc):
        """
        Initialisation of class Visibility

        Args:
            doc: input document
        """

        self.model_ele_list = None
        self.handle_list = None
        self.document = doc


    def create(self, build_ele):
        """
        Create the elements

        Args:
            build_ele:  the building element.

        Returns:
            tuple  with created elements and handles.
        """

        com_prop =  AllplanBaseElements.CommonProperties()
        com_prop.GetGlobalProperties()

        length = build_ele.Length.value

        polyhed = AllplanGeo.Polyhedron3D.CreateCuboid(length, length, length)

        views = [View2D3D ([AllplanBasisElements.ModelElement3D(com_prop, polyhed)])]
        pythonpart = PythonPart ("AllControls Example",
                                 build_ele.get_params_list(),
                                 build_ele.get_hash(),
                                 build_ele.pyp_file_name,
                                 views,
                                 common_props = com_prop)

        self.model_ele_list = pythonpart.create()

        return (self.model_ele_list, self.handle_list)
