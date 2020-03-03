"""
Script for starting the Python debugger
"""

import NemAll_Python_Utility as AllplanUtility


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

    # Delete unused arguments
    del build_ele
    del doc

    AllplanUtility.EnablePythonDebug()

    return None
