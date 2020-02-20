"""
Example for MessageBox
"""
#Allplan import
import NemAll_Python_Utility as AllplanUtil
import NemAll_Python_AllplanSettings as AllplanSett
import NemAll_Python_IFW_Input as AllplanIFW

# PyQt import
from PyQt5.QtCore import QDateTime, Qt, QTimer
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget)

from .GUI import *

#Tkinter import
from tkinter import *

#buildin import
import sys
import time
from datetime import datetime


print('Load MessageBox.py')
# AllplanUtil.EnablePythonDebug()

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
    del build_ele
    del doc

    return (list(), list())


def on_control_event(build_ele, event_id):
    """
    On control event

    Args:
        build_ele:  the building element.
        event_id:   event id of control.

    Returns:
        True/False if palette refresh is necessary
    """

    # Delete unused arguments
    del build_ele

    print ("MessageBox.py (on_control_event called, eventId: ", event_id, ")")

    if event_id == 1000:
        #ret = AllplanUtil.ShowMessageBox("Allplan version: " + AllplanSett.AllplanVersion.Version(), AllplanUtil.MB_OK)
        # ret = AllplanUtil.ShowMessageBox("Current date: " + datetime.now().strftime("%H:%M:%S"), 0)
        
        #Show Qt Window
        print("Press me clicked")
        app = QApplication(sys.argv)
        try:
            gallery = MyGui()
            gallery.show()
            sys.exit(app.exec_())
        except:
            print("Error when close window PyQt")
            pass

    else:
        print("unknown event id ", event_id)

    return False

