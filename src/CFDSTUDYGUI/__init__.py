"""
SALOME CfdStudy module implementation: main scripts, classes and methods

The interface functions of the module are in CFDSTUDYGUI (outside the module, to be found by SALOME)
CFDSTUDYGUI instantiate a clientgui object at first call. 
All the interface functions call a method of same name in the clientgui object 

clientgui.py
The class clientgui implements all the interface methods of the SALOME CfdStudy module

CLSMainWindow.py
The class CLSMainWindow is derived from QMainWindow and deals with the Qt widgets of the SALOME CfdStudy module gui.
Main methods deals with: treewidget items, popup menus, selection synchronization between tree and VTK view (meshes)

initlog.py
Implements logging. The trace system is started and the trace level set in CFDSTUDYGUI 

__init__.py
This file: only the module documentation

mw_cfdstudy_ui.py
Generated from the Qt designer file mw_cfdstudy.ui : Qt widgets nature and geometry 

CFDSTUDYGUI_DataModel.py
Implements the CFDSTUDY_DataModel, i.e. what is stored in the SALOME study and saved in the hdf study file.
Only the path of the CFD studies and case are stored.
The class CFDSTUDY_DataObject implements the SALOME Study Light objects
The class CFD_TreeWidget manages the tree items which are QTreeWidget items.
For CFD Studies and Case, the tree items are associated to SALOME Study Light objects.
The dict_object dictionary defines the different kind of items in the CFD study and case

CFDSTUDYGUI_ActionsHandler.py
The class CFDSTUDYGUI_ActionsHandler implements the actions in menus and popup menu (Tree Widget)
The actions are stored in a map (_CommonActionIdMap) with an integer key.
The actions are updated (updateActions). They can be disabled or made invisible, depending on the current state of the module and the selection.
The custom popup menu of the tree widget items are build depending on the current selection.

CFDSTUDYGUI_SolverGUI.py
The class CFDSTUDYGUI_SolverGUI provides an interface to the Solvers GUIs (Code Saturne / neptune_cfd). Only tested with Code_Saturne...

CFDSTUDYOTURNS_StudyInterface.py
Class used for an OpenTurns study within SALOME_CFD

utilstudy.py
The DumpMesh function explore the SALOME study to find a loaded mesh and all its groups which have an entry in the study
"""
