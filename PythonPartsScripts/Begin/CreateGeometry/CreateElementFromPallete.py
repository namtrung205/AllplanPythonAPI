"""
Example for MessageBox
"""
#Allplan import
import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_Utility as AllplanUtil

#buildin import
import sys
import time
from datetime import datetime
import math

print('CreateElementFromPallete.py')

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

    Returns:
        Tuple with created elements, handles and (optional) reinforcement.
    """

    # Delete unused arguments

    element = BoxSteel(doc)
    return element.create(build_ele)

class CreateBRepSwept3DService():

    # Contructor method
    def __init__(self, doc):
        """
        Initialisation of class BRepBuilder
        Args:
            doc: input document
        """

        self.model_ele_list = [] # Danh sách chứa các model sẽ được tạo ra từ script
        self.handle_list = [] # Danh sách các handle(điểm kéo thả giống gripPoint autocad)
        self.document = doc # Current Document

        #Get, set các thông số thuộc tính chung cho các phần tử
        self.com_prop = AllplanBaseElements.CommonProperties() # Các thuộc tính chung của bản vẽ hiện hành (nét, đường, màu, layer....)
        self.com_prop.GetGlobalProperties() # Hàm lấy các thuộc tính chung hiện hành(global)
        self.com_prop_help1 = AllplanBaseElements.CommonProperties() # Các thuộc tính chung của BaseElements
        self.com_prop_help1.GetGlobalProperties() # ....
        self.com_prop_help1.Color = 6 # Các thuộc tính được set lại
        self.com_prop_help2 = AllplanBaseElements.CommonProperties()
        self.com_prop_help2.GetGlobalProperties()
        self.com_prop_help2.Color = 7
        self.show_elements = True

    # Hàm dựng chung
    def create(self, build_ele):
        """
        Create the elements

        Args:
            build_ele:  the building element.
        Returns:
            tuple  with created elements and handles. 
            => Trả về 1 tuple chứa danh sách các elements và các handles được tạo ra
        """

        #self.show_elements = build_ele.ShowElements.value 
        self.show_elements = True # Set cờ True để luôn hiển thị

        # Trong ví dụ này chỉ thể hiện 1 hàm dựng hình duy nhất(Swept), các hàm còn lại tham chiếu trong thư mục ETC 
        #self.create_swept_breps(build_ele)
        self.create_extrude_breps()
        #self.create_frustum_pyramid()

        return (self.model_ele_list, self.handle_list)

    # Hàm dựng hình chính
    def create_swept_breps(self):
        """
        Create swept breps
        """

        #------------------------ next brep (axis sweep)
        polyline = AllplanGeo.Polyline3D()
        polyline += AllplanGeo.Point3D(100, 0, 0)
        polyline += polyline.GetLastPoint() + AllplanGeo.Vector3D(100, 0, 0)
        polyline += polyline.GetLastPoint() + AllplanGeo.Vector3D(100, 0, 50)
        polyline += polyline.GetLastPoint() + AllplanGeo.Vector3D(0, 0, 50)
        polyline += polyline.GetStartPoint()
        profile = polyline

        arc = AllplanGeo.Arc3D(AllplanGeo.Point3D(0, 0, 0),
                               AllplanGeo.Vector3D(1, 0, 0),
                               AllplanGeo.Vector3D(0, 0, 1),
                               400, 400, 0, math.pi + math.pi / 2, True)
        path = AllplanGeo.BSpline3D.CreateArc3D(arc)

        axis_line = AllplanGeo.Line3D(0, 0, 0, 0, 0, 150)
        zaxis = AllplanGeo.Vector3D(0, 0, 1)

        err, brep = AllplanGeo.CreateSweptBRep3D(profile, path, False, zaxis)
        self.create_elements(err, brep)

    # Tranform
    def translate(self, element, trans_vector):
        """
        Translate element by translation vector
        """
        matrix = AllplanGeo.Matrix3D()
        matrix.Translate(trans_vector)
        return AllplanGeo.Transform(element, matrix)

    def create_extrude_breps(self): # Swept bởi Vector

        # Create Profile 1
        polyline = AllplanGeo.Polyline3D()
        polyline += AllplanGeo.Point3D(-50, -50, 0)
        polyline += polyline.GetLastPoint() + AllplanGeo.Vector3D(100, 0, 0)
        polyline += polyline.GetLastPoint() + AllplanGeo.Vector3D(0, 100, 0)
        polyline += polyline.GetLastPoint() + AllplanGeo.Vector3D(-100, 0, 0)
        polyline += polyline.GetStartPoint()

        profile = self.translate(polyline, AllplanGeo.Vector3D(0,0,0))


        self.model_ele_list.append(AllplanBasisElements.ModelElement3D(self.com_prop, profile))

        poly_list = AllplanGeo.Polyline3DList()
        poly_list.append(profile)

        # Path to extrude
        path = AllplanGeo.Polyline3D()
        start_pnt = AllplanGeo.Point3D(100,100,100)
        path += start_pnt
        path += start_pnt + AllplanGeo.Point3D(0, 0, 5000)

        err_1, brep_1 = AllplanGeo.CreateSweptPolyhedron3D(poly_list, path, True, True, AllplanGeo.Vector3D())


        # Create Profile 2
        polyline_2 = AllplanGeo.Polyline3D()
        polyline_2 += AllplanGeo.Point3D(-60, -60, 0)
        polyline_2 += polyline_2.GetLastPoint() + AllplanGeo.Vector3D(120, 0, 0)
        polyline_2 += polyline_2.GetLastPoint() + AllplanGeo.Vector3D(0, 120, 0)
        polyline_2 += polyline_2.GetLastPoint() + AllplanGeo.Vector3D(-120, 0, 0)
        polyline_2 += polyline_2.GetStartPoint()
        profile_2 = self.translate(polyline_2, AllplanGeo.Vector3D(0,0,0))

        self.model_ele_list.append(AllplanBasisElements.ModelElement3D(self.com_prop, profile_2))

        poly_list_2 = AllplanGeo.Polyline3DList()
        poly_list_2.append(profile_2)


        # Path to extrude 2
        path_2 = AllplanGeo.Polyline3D()
        start_pnt_2 = AllplanGeo.Point3D(100,100,100)
        path_2 += start_pnt_2
        path_2 += start_pnt_2 + AllplanGeo.Point3D(0, 0, 5000)

        err_2, brep_2 = AllplanGeo.CreateSweptPolyhedron3D(poly_list_2, path_2, True, True, AllplanGeo.Vector3D())


        ## Subtract Object
        err_Sub, brep_Sub = AllplanGeo.MakeSubtraction(brep_2, brep_1)

        edges = AllplanUtil.VecSizeTList()

        numberEdge = int(brep_Sub.GetEdgesCount())
        for i in range(0, numberEdge):
            edges.append(i)

        # Fillet
        err_Fillet, brep_Fillet = AllplanGeo.FilletCalculus3D.Calculate(brep_Sub, edges, 5.0, True)
        self.create_elements(err_Fillet, brep_Fillet)

    #Tao hinh Chop cut
    def create_frustum_pyramid(self):
        bottomPlane = AllplanGeo.Plane3D()
        bottomPlane.SetVector(AllplanGeo.Vector3D(0,0,1))
        bottomPlane.SetPoint(AllplanGeo.Point3D())
        err, brep = AllplanGeo.CreateFrustumOfPyramid(1000, 1000, 600, 200, bottomPlane)
        self.create_elements(err, brep)

    def create_elements(self, err, brep):
        """
        Create Brep element and helper elements
        """
        if not err and brep.IsValid:
            self.model_ele_list.append(AllplanBasisElements.ModelElement3D(self.com_prop, brep))
        else:
            print("Error: ")

class BoxSteel():
    # Contructor method
    def __init__(self, doc):
        """
        Initialisation of class BRepBuilder
        Args:
            doc: input document
        """
        self.model_ele_list = [] # Danh sách chứa các model sẽ được tạo ra từ script
        self.handle_list = [] # Danh sách các handle(điểm kéo thả giống gripPoint autocad)
        self.document = doc # Current Document

        #Get, set các thông số thuộc tính chung cho các phần tử
        self.com_prop = AllplanBaseElements.CommonProperties() # Các thuộc tính chung của bản vẽ hiện hành (nét, đường, màu, layer....)
        self.com_prop.GetGlobalProperties() # Hàm lấy các thuộc tính chung hiện hành(global)

    def create(self, build_ele):
        """
        Create the elements

        Args:
            build_ele:  the building element.
        Returns:
            tuple  with created elements and handles. 
            => Trả về 1 tuple chứa danh sách các elements và các handles được tạo ra
        """
        #Get parameter from palette
        height = build_ele.Height.value
        OD = build_ele.OD.value
        thickness = build_ele.Thickness.value
        radFillet = build_ele.RadFillet.value
        self.create_extrude_box_steel(height, OD, thickness, radFillet)
        return (self.model_ele_list, self.handle_list)

    # Tranform
    def translate(self, element, trans_vector):
        """
        Translate element by translation vector
        """
        matrix = AllplanGeo.Matrix3D()
        matrix.Translate(trans_vector)
        return AllplanGeo.Transform(element, matrix)

    #Create Solid
    def create_extrude_box_steel(self, height, OD, thickness, radFillet): # Swept bởi Vector

        # Path to extrude
        path = AllplanGeo.Polyline3D()
        start_pnt = AllplanGeo.Point3D(0,0,0)
        path += start_pnt
        path += start_pnt + AllplanGeo.Point3D(0, 0, height)

        # Create Profile 1
        polyline_out = AllplanGeo.Polyline3D()
        polyline_out += AllplanGeo.Point3D(-OD/2, -OD/2, 0)
        polyline_out += polyline_out.GetLastPoint() + AllplanGeo.Vector3D(OD, 0, 0)
        polyline_out += polyline_out.GetLastPoint() + AllplanGeo.Vector3D(0, OD, 0)
        polyline_out += polyline_out.GetLastPoint() + AllplanGeo.Vector3D(-OD, 0, 0)
        polyline_out += polyline_out.GetStartPoint()

        profile_out = self.translate(polyline_out, AllplanGeo.Vector3D(0,0,0))

        #self.model_ele_list.append(AllplanBasisElements.ModelElement3D(self.com_prop, profile_out))

        poly_list_out = AllplanGeo.Polyline3DList()
        poly_list_out.append(profile_out)

        err_out, solid_out = AllplanGeo.CreateSweptPolyhedron3D(poly_list_out, path, True, True, AllplanGeo.Vector3D())

        # Create Profile 2
        ID = OD-thickness*2
        polyline_in = AllplanGeo.Polyline3D()
        polyline_in += AllplanGeo.Point3D(-ID/2, -ID/2, 0)
        polyline_in += polyline_in.GetLastPoint() + AllplanGeo.Vector3D(ID, 0, 0)
        polyline_in += polyline_in.GetLastPoint() + AllplanGeo.Vector3D(0, ID, 0)
        polyline_in += polyline_in.GetLastPoint() + AllplanGeo.Vector3D(-ID, 0, 0)
        polyline_in += polyline_in.GetStartPoint()

        profile_in = self.translate(polyline_in, AllplanGeo.Vector3D(0,0,0))

        self.model_ele_list.append(AllplanBasisElements.ModelElement3D(self.com_prop, profile_in))

        poly_list_in = AllplanGeo.Polyline3DList()
        poly_list_in.append(profile_in)

        err_in, solid_in = AllplanGeo.CreateSweptPolyhedron3D(poly_list_in, path, True, True, AllplanGeo.Vector3D())

        # Subtract Object
        err, solid_box_steel = AllplanGeo.MakeSubtraction(solid_out, solid_in)

        #Edge fillet
        edges = AllplanUtil.VecSizeTList()
        numberEdge = int(solid_box_steel.GetEdgesCount())
        for i in range(0, numberEdge):
            edges.append(i)

        # Fillet
        err_Fillet, solid_box_steel_fillet = AllplanGeo.FilletCalculus3D.Calculate(solid_box_steel, edges, radFillet, True)
        self.create_elements(err_Fillet, solid_box_steel_fillet)

    def create_elements(self, err, brep):
        """
        Create Brep element and helper elements
        """
        if not err and brep.IsValid:
            self.model_ele_list.append(AllplanBasisElements.ModelElement3D(self.com_prop, brep))
        else:
            print("Error: Cannot Create SteelBox")