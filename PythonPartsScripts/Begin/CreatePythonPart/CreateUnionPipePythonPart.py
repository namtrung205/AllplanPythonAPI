
"""
Script for Table
"""
import hashlib
import math

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import GeometryValidate as GeometryValidate

from HandleDirection import HandleDirection
from HandleProperties import HandleProperties
from PythonPart import View2D3D, PythonPart, PythonPartGroup


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

def move_handle(build_ele, handle_prop, input_pnt, doc):
    """
    Modify the element geometry by handles

    Args:
        build_ele:  the building element.
        handle_prop handle properties
        input_pnt:  input point
        doc:        input document
    """

    build_ele.change_property(handle_prop, input_pnt)
    return create_element(build_ele, doc)

def create_element(build_ele, doc):
    """
    Creation of element

    Args:
        build_ele: the building element.
        doc:       input document
    """
    del doc # param not needed

    common_props = AllplanBaseElements.CommonProperties()
    common_props.GetGlobalProperties()

    #-----------Pipe
    unionPipe = UnionPipe(build_ele.Length.value, build_ele.Diameter.value, build_ele.Thickness.value,\
                         build_ele.IncludePad.value, build_ele.PadDiameter.value, build_ele.PadThickness.value,\
                         build_ele.Angle.value,\
                         build_ele.TurnRadius.value, build_ele.TurnAngle.value)
    if not unionPipe.is_valid():
        return ([], [])

    handle_list = unionPipe.create_handles()
    unionPipe_views = [View2D3D ([AllplanBasisElements.ModelElement3D(common_props, unionPipe.create())])]
    pythonpartUnionPipe = PythonPart ("UnionPipe",
                             parameter_list = unionPipe.get_params_list(),
                             hash_value = unionPipe.hash(),
                             python_file = unionPipe.filename(),
                             views = unionPipe_views)
    ##-----------CenterLine
    #centerLinePipe = CenterLinePipe(build_ele.Length.value)
    #if not centerLinePipe.is_valid():
    #    return ([], [])

    #handle_list = centerLinePipe.create_handles()
    #centerLinePipe_views = [View2D3D ([AllplanBasisElements.ModelElement3D(common_props, centerLinePipe.create())])]
    #pythonpartCenterLinePipe = PythonPart ("CenterLinePipe",
    #                         parameter_list = centerLinePipe.get_params_list(),
    #                         hash_value = centerLinePipe.hash(),
    #                         python_file = centerLinePipe.filename(),
    #                         views = centerLinePipe_views)

    group_elems = []
    group_elems.append(pythonpartUnionPipe)
    #group_elems.append(pythonpartPipe)

    #Define one python part group for this suite
    pythonpartgroup = PythonPartGroup ("PipeGroup", build_ele.get_params_list(), build_ele.get_hash(),
                                       build_ele.pyp_file_name, group_elems)
    model_elem_list = pythonpartgroup.create()

    return (model_elem_list, handle_list)

def deg_to_rad(angleDeg):
    return float(angleDeg/(180/math.pi))

class UnionPipe():
    """
    Definition of class Pipe
    """

    def __init__(self, length = 50.0, diameter = 100.0, thickness = 2.0, includePad = True, padDiameter = 130, padThickness = 5, angle = 0, turnRadius = 50, turnAngle = math.pi/2):
        """
        Initialisation of class Pipe
        """
        self.length = length
        self.diameter = diameter
        self.thickness = thickness

        self.includePad = includePad
        self.padDiameter = padDiameter
        self.padThickness = padThickness

        self.angle = deg_to_rad(angle)

        self.turnRadius = turnRadius
        self.turnAngle = deg_to_rad(turnAngle)

        self.centerLine = None
        self.body = None

    def get_params_list(self):
        """
        Append all parameters as parameter list

        Returns: param list
        """
        param_list = []
        param_list.append ("Length = %s\n" % self.length)
        param_list.append ("Diameter = %s\n" % self.diameter)
        param_list.append ("Thickness = %s\n" % self.thickness)
        param_list.append ("PadDiameter = %s\n" % self.padDiameter)
        param_list.append ("PadThickness = %s\n" % self.padThickness)
        param_list.append ("Angle = %s\n" % self.angle)
        param_list.append ("TurnRadius = %s\n" % self.turnRadius)
        param_list.append ("TurnAngle = %s\n" % self.turnAngle)

        return param_list

    def __repr__(self):
        return 'UnionPipe(length=%s, diameter=%s, thickness=%s,  padDiameter=%s, padThickness=%s, angle=%s, turnRadius=%s, turnAngle=%s,' \
            % (self.length, self.diameter, self.thickness, self.padDiameter, self.padThickness, self.angle, self.turnRadius, self.turnAngle)

    def hash (self):
        """
        Calculate hash value for script

        Returns:
            Hash string
        """
        param_string = self.__repr__()
        hash_val = hashlib.sha224(param_string.encode('utf-8')).hexdigest()
        return hash_val

    def filename(self):
        """
        Python script filename

        Returns:
            Script filename
        """
        return "CreateUnionPipePythonPart.py"

    def is_valid(self):
        """
        Check for valid values
        """
        if self.length <= 0 or self.diameter <= 0 or self.thickness <= 0 or self.padDiameter<=0 or self.padThickness<=0 or self.turnRadius < self.diameter/2:
            return False
        return True

    def create(self):
        """
        Create a Table
        """
        if not self.is_valid():
            return []

        #-----Revolve Solid
        profiles = []
        profile = AllplanGeo.Arc3D(AllplanGeo.Point3D(0,0,0), AllplanGeo.Vector3D(self.diameter/2,0,0), AllplanGeo.Vector3D(0,0,1),self.diameter/2,self.diameter/2,0,math.pi*2)
        profiles.append(profile)

        axisRev = AllplanGeo.Axis3D(AllplanGeo.Point3D(self.turnRadius,0,0), AllplanGeo.Vector3D(0,1,0))

        err, unionRevBrep_solid = AllplanGeo.CreateRevolvedBRep3D(profiles, axisRev,AllplanGeo.Angle(self.turnAngle),True, 1)

        #-----Revolve Void
        profilesVoid = []
        profileVoid = AllplanGeo.Arc3D(AllplanGeo.Point3D(0,0,0), AllplanGeo.Vector3D(self.diameter/2,0,0), AllplanGeo.Vector3D(0,0,1),self.diameter/2-self.thickness,self.diameter/2-self.thickness,0,math.pi*2)
        profilesVoid.append(profileVoid)
        err, unionRevBrep_void = AllplanGeo.CreateRevolvedBRep3D(profilesVoid, axisRev,AllplanGeo.Angle(self.turnAngle),True, 1)

        err, unionRevBrep = AllplanGeo.MakeSubtraction(unionRevBrep_solid, unionRevBrep_void)


        matrixRot = AllplanGeo.Matrix3D()
        matrixRot.SetRotation(AllplanGeo.Line3D(0,0,0,0,0,1), AllplanGeo.Angle(self.angle))

        unionRevBrepRot = AllplanGeo.Transform(unionRevBrep,matrixRot)

        self.body = unionRevBrepRot
        return self.body

    def create_handles(self):
        """
        Create handles

        Returns:
            List of HandleProperties
        """

        #------------------ Create the handle

        handle_list = [HandleProperties("Handle",
                                        AllplanGeo.Point3D(self.diameter/2, 0, 0),
                                        AllplanGeo.Point3D(0, 0, 0),
                                        [("Angle", HandleDirection.angle),],
                                         HandleDirection.angle),
                      ]
        return handle_list

#class CenterLinePipe():
#    """
#    Definition of class Pipe
#    """

#    def __init__(self, length = 1000.0):
#        """
#        Initialisation of class Pipe
#        """
#        self.length = length
#        self.centerLine = None


#    def get_params_list(self):
#        """
#        Append all parameters as parameter list

#        Returns: param list
#        """
#        param_list = []
#        param_list.append ("Length = %s\n" % self.length)
#        return param_list

#    def __repr__(self):
#        return 'Pipe(length=%s,)' \
#            % (self.length)

#    def hash (self):
#        """
#        Calculate hash value for script

#        Returns:
#            Hash string
#        """
#        param_string = self.__repr__()
#        hash_val = hashlib.sha224(param_string.encode('utf-8')).hexdigest()
#        return hash_val

#    def filename(self):
#        """
#        Python script filename

#        Returns:
#            Script filename
#        """
#        return "CreatePipePythonPart.py"

#    def is_valid(self):
#        """
#        Check for valid values
#        """
#        if self.length <= 0:
#            return False
#        return True

#    def create(self):
#        """
#        Create a Table
#        """
#        if not self.is_valid():
#            return []

#        point1 = AllplanGeo.Point3D(0, 0, 0)
#        #-----------------Create center line
#        line = AllplanGeo.Line3D(point1, AllplanGeo.Point3D(0, 0, self.length))

#        self.centerLine = line
#        return self.centerLine

#    def create_handles(self):
#        """
#        Create handles

#        Returns:
#            List of HandleProperties
#        """

#        #------------------ Create the handle

#        handle_list = [HandleProperties("Handle",
#                                        AllplanGeo.Point3D(0, 0,self.length),
#                                        AllplanGeo.Point3D(0, 0, 0),
#                                        [("Length", HandleDirection.z_dir),],
#                                         HandleDirection.z_dir),
#                      ]
#        return handle_list
