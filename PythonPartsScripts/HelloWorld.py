"""
Hello world template
"""

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_ArchElements as AllplanArch

# Print some information
print('Load HelloWorld.py')


# Method for checking the supported versions
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


# Method for element creation
def create_element(build_ele, doc):
    """
    Creation of element

    Args:
        build_ele: the building element.
        doc:       input document

    Returns:
            tuple  with created elements, handles and (otional) reinforcement.
    """

    # Delete unused arguments
    del doc

    # Access the parameter property from *.pyp file
    length = build_ele.Length.value
    # Create a 2d line
    line = AllplanGeo.Line2D(100, 100, 1000, 0)
    # Define common style properties
    common_props = AllplanBaseElements.CommonProperties()
    common_props.GetGlobalProperties()
    # Create a 2D ModelElement instance and add it to elements list
    model_elem_list = [AllplanBasisElements.ModelElement2D(common_props, line)]
    # Define the handles list
    handle_list = []

    p1 = AllplanGeo.Point3D(0,0,0)
    p2 = AllplanGeo.Point3D(2500,0,0)

    line3d = AllplanGeo.Line3D(p1, p2)
    model_elem_list.append(AllplanBasisElements.ModelElement3D(common_props, line3d))



    # Return a tuple with elements list and handles list
    return (model_elem_list, handle_list)
