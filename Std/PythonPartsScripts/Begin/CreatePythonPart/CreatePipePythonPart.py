
"""
Script for Table
"""
import hashlib

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
    pipe = Pipe(build_ele.Length.value, build_ele.Diameter.value, build_ele.Thickness.value, build_ele.IncludePad.value, build_ele.PadDiameter.value, build_ele.PadThickness.value,)
    if not pipe.is_valid():
        return ([], [])

    #handle_list = pipe.create_handles()
    pipe_views = [View2D3D ([AllplanBasisElements.ModelElement3D(common_props, pipe.create())])]
    pythonpartPipe = PythonPart ("Pipe",
                             parameter_list = pipe.get_params_list(),
                             hash_value = pipe.hash(),
                             python_file = pipe.filename(),
                             views = pipe_views)
    #-----------CenterLine
    centerLinePipe = CenterLinePipe(build_ele.Length.value)
    if not centerLinePipe.is_valid():
        return ([], [])

    handle_list = centerLinePipe.create_handles()
    centerLinePipe_views = [View2D3D ([AllplanBasisElements.ModelElement3D(common_props, centerLinePipe.create())])]
    pythonpartCenterLinePipe = PythonPart ("CenterLinePipe",
                             parameter_list = centerLinePipe.get_params_list(),
                             hash_value = centerLinePipe.hash(),
                             python_file = centerLinePipe.filename(),
                             views = centerLinePipe_views)

    group_elems = []
    group_elems.append(pythonpartCenterLinePipe)
    group_elems.append(pythonpartPipe)

    # Define one python part group for this suite
    pythonpartgroup = PythonPartGroup ("PipeGroup", build_ele.get_params_list(), build_ele.get_hash(),
                                       build_ele.pyp_file_name, group_elems)
    model_elem_list = pythonpartgroup.create()
    print(pythonpartgroup._pythonparts[0]._parameter_list)

    matrix = AllplanGeo.Matrix3D()

    axis = AllplanGeo.Line3D(AllplanGeo.Point3D(0,0,0), AllplanGeo.Point3D(0,1,0))
    angle = AllplanGeo.Angle(3.14)
    matrix.Rotation(axis, angle)
    
    #AllplanBaseElements.ElementTransform(matrix, model_elem_list)

    return (model_elem_list, handle_list)

class Pipe():
    """
    Definition of class Pipe
    """

    def __init__(self, length = 1000.0, diameter = 100.0, thickness = 2.0, includePad = False, padDiameter = 130, padThickness = 5):
        """
        Initialisation of class Pipe
        """
        self.length = length
        self.diameter = diameter
        self.thickness = thickness

        self.includePad = includePad
        self.padDiameter = padDiameter
        self.padThickness = padThickness

        self.centerLine = None
        self.pipe = None

    def get_params_list(self):
        """
        Append all parameters as parameter list

        Returns: param list
        """
        param_list = []
        param_list.append ("Length = %s\n" % self.length)
        param_list.append ("Diameter = %s\n" % self.diameter)
        param_list.append ("Thickness = %s\n" % self.thickness)
        param_list.append ("IncludePad = %s\n" % self.includePad)
        param_list.append ("PadDiameter = %s\n" % self.padDiameter)
        param_list.append ("PadThickness = %s\n" % self.padThickness)
        return param_list

    def __repr__(self):
        return 'Pipe(length=%s, diameter=%s, thickness=%s, includePad=%s, padDiameter=%s, padThickness=%s,' \
            % (self.length, self.diameter, self.thickness, self.includePad, self.padDiameter, self.padThickness)

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
        return "CreatePipePythonPart.py"

    def is_valid(self):
        """
        Check for valid values
        """
        if self.length <= 0 or self.diameter <= 0 or self.thickness <= 0 or self.padDiameter<=0 or self.padThickness<=0:
            return False
        return True

    def create(self):
        """
        Create a Table
        """
        if not self.is_valid():
            return []

        point1 = AllplanGeo.Point3D(0, 0, 0)
        #-----------------Create center line
        line = AllplanGeo.Line3D(point1, AllplanGeo.Point3D(0, 0, self.length))

        #------------------ Create the pipe solid body
        axisPlace = AllplanGeo.AxisPlacement3D(point1,AllplanGeo.Vector3D(1,0,0),AllplanGeo.Vector3D(0,0,1))
        pipeOut = AllplanGeo.BRep3D.CreateCylinder(axisPlace, self.diameter, self.length, True, True)


        brepListToUnion =  AllplanGeo.BRep3DList()
        if self.includePad:
            pipePadBot = AllplanGeo.BRep3D.CreateCylinder(axisPlace, self.padDiameter, self.padThickness, True, True);
            if pipePadBot.IsValid():
                brepListToUnion.append(pipePadBot)

            axisPlaceRe = AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(0, 0, self.length), AllplanGeo.Vector3D(1,0,0),AllplanGeo.Vector3D(0,0,-1))
            pipePadTop = AllplanGeo.BRep3D.CreateCylinder(axisPlaceRe, self.padDiameter, self.padThickness, True, True);
            if pipePadTop.IsValid():
                brepListToUnion.append(pipePadTop)

        #----union
        pipeSolid = pipeOut
        if self.includePad:
            err, pipeSolid = AllplanGeo.MakeUnion(pipeOut, brepListToUnion)
        else:
            pipeSolid = pipeOut

        inDiameter = self.diameter-2*self.thickness
        pipeVoid = AllplanGeo.BRep3D.CreateCylinder(axisPlace, inDiameter, self.length, True, True)


        pipe = None
        if pipeSolid.IsValid() and pipeVoid.IsValid():
            err, pipe = AllplanGeo.MakeSubtraction(pipeSolid, pipeVoid)

        self.pipe = pipe
        return self.pipe

    def create_handles(self):
        """
        Create handles

        Returns:
            List of HandleProperties
        """

        #------------------ Create the handle

        handle_list = [HandleProperties("Handle",
                                        AllplanGeo.Point3D(0, 0,self.length),
                                        AllplanGeo.Point3D(0, 0, 0),
                                        [("Length", HandleDirection.z_dir),],
                                         HandleDirection.z_dir),
                      ]
        return handle_list

class CenterLinePipe():
    """
    Definition of class Pipe
    """

    def __init__(self, length = 1000.0):
        """
        Initialisation of class Pipe
        """
        self.length = length
        self.centerLine = None


    def get_params_list(self):
        """
        Append all parameters as parameter list

        Returns: param list
        """
        param_list = []
        param_list.append ("Length = %s\n" % self.length)
        return param_list

    def __repr__(self):
        return 'Pipe(length=%s,)' \
            % (self.length)

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
        return "CreatePipePythonPart.py"

    def is_valid(self):
        """
        Check for valid values
        """
        if self.length <= 0:
            return False
        return True

    def create(self):
        """
        Create a Table
        """
        if not self.is_valid():
            return []

        point1 = AllplanGeo.Point3D(0, 0, 0)
        #-----------------Create center line
        line = AllplanGeo.Line3D(point1, AllplanGeo.Point3D(0, 0, self.length))

        self.centerLine = line
        return self.centerLine

    def create_handles(self):
        """
        Create handles

        Returns:
            List of HandleProperties
        """
        #------------------ Create the handle
        handle_list = [HandleProperties("Handle",
                                        AllplanGeo.Point3D(0, 0,self.length),
                                        AllplanGeo.Point3D(0, 0, 0),
                                        [("Length", HandleDirection.z_dir),],
                                         HandleDirection.z_dir),
                      ]
        return handle_list