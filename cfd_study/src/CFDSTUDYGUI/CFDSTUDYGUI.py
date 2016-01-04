# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------

# This file is part of Code_Saturne, a general-purpose CFD tool.
#
# Copyright (C) 1998-2016 EDF S.A.
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51 Franklin
# Street, Fifth Floor, Boston, MA 02110-1301, USA.

#-------------------------------------------------------------------------------

"""
CFDSTUDY
========

Main file of the CFD_STUDY module. Defines the standard SALOME callback.
"""

#-------------------------------------------------------------------------------
# Standard modules
#-------------------------------------------------------------------------------

import os, string
import logging

#-------------------------------------------------------------------------------
# Third-party modules
#-------------------------------------------------------------------------------

from PyQt4.QtGui import QDialog, QMessageBox, QDockWidget, QCursor, QApplication, QTabWidget
from PyQt4.QtCore import Qt, QObject, SIGNAL

#-------------------------------------------------------------------------------
# Salome modules
#-------------------------------------------------------------------------------

import SalomePyQt
from SalomePyQt import WT_ObjectBrowser, WT_PyConsole, WT_LogWindow
import SALOMEDS
import SALOMEDS_Attributes_idl
import salome, salome_version

#-------------------------------------------------------------------------------
# Application modules
#-------------------------------------------------------------------------------

import CFDSTUDYGUI_ActionsHandler
import CFDSTUDYGUI_DataModel
import CFDSTUDYGUI_Commons
import CFDSTUDYGUI_DesktopMgr
import CFDSTUDYGUI_SolverGUI

from CFDSTUDYGUI_Commons import sg, sgPyQt
from CFDSTUDYGUI_Commons import CFD_Saturne, CFD_Neptune
from CFDSTUDYGUI_Commons import CheckCFD_CodeEnv

#-------------------------------------------------------------------------------
# log config
#-------------------------------------------------------------------------------

logging.basicConfig()
log = logging.getLogger("CFDSTUDYGUI")
log.setLevel(logging.NOTSET)

#-------------------------------------------------------------------------------
# Global definitions
#-------------------------------------------------------------------------------
__MODULE_NAME__ = "CFDSTUDY"
studyId = salome.myStudyId
d_activation = {}

# Desktop manager: instance of CFDSTUDYGUI_DesktopMgr class to store the SALOME Workspace
_DesktopMgr = CFDSTUDYGUI_DesktopMgr.CFDSTUDYGUI_DesktopMgr()

# ObjectTR is a convenient object for traduction purpose
ObjectTR = QObject()

DEFAULT_EDITOR_NAME = ObjectTR.tr("CFDSTUDY_PREF_EDITOR")

#-------------------------------------------------------------------------------
# Callback GUI functions
#-------------------------------------------------------------------------------

def initialize():
    """
    This method is called when GUI module is being created and initialized.
    """
    # nothing to do here.
    log.debug("initialize")
    if not sgPyQt.hasSetting( "CFDSTUDY", "ExternalEditor"):
        sgPyQt.addSetting( "CFDSTUDY", "ExternalEditor", DEFAULT_EDITOR_NAME )
    pass


def windows():
    """
    This method is called when GUI module is being created
    and initialized.
    Should return a layout of the SALOME dockable windows id's
    needed to be opened when module is activated.

    @return: layout of the SALOME dockable windows
    @rtype: C{Dictionary}
    """
    log.debug("windows")

    winMap = {}
    winMap[ WT_ObjectBrowser ] = Qt.LeftDockWidgetArea
    winMap[ WT_PyConsole ]     = Qt.BottomDockWidgetArea
    #winMap[ WT_LogWindow ]     = Qt.BottomDockWidgetArea
    return winMap


def closeStudy(aStudyId) :
    """
    This method is called when salome study is closed (Salome desktop button File -> close -> close w/o saving button) and Salome Main window desktop is already available
    """
    if salome_version.getVersion() >= '7.5.0' :
        CFDSTUDYGUI_SolverGUI._c_CFDGUI.cleanAllDock(sgPyQt.getDesktop())


def views():
    """
    This method is called when GUI module is being created and initialized.
    Should return a list of the SALOME view window types
    needed to be opened when module is activated.
    cf. SALOME_PYQT_Module.cxx: PyObjWrapper

    @return: list of the SALOME view window types
    @rtype: C{String} or C{list} of C{String}
    """
    log.debug("views")
    winList = "VTKViewer"
    #winList = "OCCViewer"
    #winList = "Plot2d"
    #winList = ""

    return winList


def setWorkSpace(ws):
    """
    Stores the SALOME Workspace I{ws} into the Desktop Manager.

    @type ws: C{QWidget}
    @param ws: main window's central widget
    """
    log.debug("setWorkSpace")

    dsk = sgPyQt.getDesktop()
    _DesktopMgr.setWorkspace(dsk, ws)
    ActionHandler = _DesktopMgr.getActionHandler(dsk)


def createPreferences():
    """
    Manages the preferences QDialog of the module.
    """
    log.debug("createPreferences")
    sgPyQt = CFDSTUDYGUI_DataModel.sgPyQt
    genTab = sgPyQt.addPreference(ObjectTR.tr("CFDSTUDY_PREF_GEN_GROUP"))
    editorGroup = sgPyQt.addPreference("Editor",genTab)
    editor      = sgPyQt.addPreference("External Editor",editorGroup,SalomePyQt.PT_String, "CFDSTUDY","ExternalEditor")
    Reader      = sgPyQt.addPreference("External Reader",editorGroup,SalomePyQt.PT_String, "CFDSTUDY","ExternalReader")


def preferenceChanged( section, setting ):
    log.debug("preferenceChanged(): %s / %s" % ( section, setting ))
    pass


def activate():
    """
    This method is called when GUI module is being activated.

    @rtype: C{True} or C{False}
    @return: C{True} only if the activation is successful.
    """
    log.debug("activate")
    global d_activation, studyId

    dsk = sgPyQt.getDesktop()
    studyId = sgPyQt.getStudyId()
    dsk.setTabPosition(Qt.RightDockWidgetArea,QTabWidget.South)
    dsk.setTabPosition(Qt.LeftDockWidgetArea,QTabWidget.South)

    if salome_version.getVersion() <= '7.4.0' :
        if salome.myStudy.FindComponent(__MODULE_NAME__) == None :
            CFDSTUDYGUI_SolverGUI._c_CFDGUI.cleanAllDock(sgPyQt.getDesktop())
            log.debug("activate ->  CFDSTUDYGUI_SolverGUI._c_CFDGUI.d_CfdCases = %s" % CFDSTUDYGUI_SolverGUI._c_CFDGUI.d_CfdCases)
    # instance of the CFDSTUDYGUI_ActionsHandler class for the current desktop
    ActionHandler = _DesktopMgr.getActionHandler(dsk)

    if studyId not in d_activation.keys():
        d_activation[studyId] = 1

    if d_activation[studyId] == 1:
        d_activation[studyId] = 0
        env_saturne, mess1 = CheckCFD_CodeEnv(CFD_Saturne)
        env_neptune, mess2 = CheckCFD_CodeEnv(CFD_Neptune)

        log.debug("activate -> env_saturne = %s" % env_saturne)
        log.debug("activate -> env_neptune = %s" % env_neptune)

        if not env_saturne and not env_neptune:
            QMessageBox.critical(ActionHandler.dskAgent().workspace(),
                                 "Error", mess1, QMessageBox.Ok, 0)
            QMessageBox.critical(ActionHandler.dskAgent().workspace(),
                                 "Error", mess2, QMessageBox.Ok, 0)
            d_activation[studyId] = 1
            return False

        if env_neptune:
            if mess2 != "":
                Error = "Error: "+ ObjectTR.tr("CFDSTUDY_INVALID_ENV")
                QMessageBox.critical(ActionHandler.dskAgent().workspace(),
                                     Error, mess2, QMessageBox.Ok, 0)
                d_activation[studyId] = 1
                return False
            else:
                ActionHandler.DialogCollector.InfoDialog.setCode(env_saturne, env_neptune)

        elif env_saturne:
            if mess1 != "":
                Error = "Error: "+ ObjectTR.tr("CFDSTUDY_INVALID_ENV")
                QMessageBox.critical(ActionHandler.dskAgent().workspace(),
                                     Error, mess1, QMessageBox.Ok, 0)
                d_activation[studyId] = 1
                return False
            else:
                ActionHandler.DialogCollector.InfoDialog.setCode(env_saturne, False)

        ActionHandler.slotStudyLocation()

    ActionHandler.connect(ActionHandler._SalomeSelection,
                          SIGNAL('currentSelectionChanged()'),
                          ActionHandler.updateActions)

    ActionHandler.connectSolverGUI()
    ActionHandler.updateObjBrowser()

    # Hide the Python Console window layout
    for dock in sgPyQt.getDesktop().findChildren(QDockWidget):
        dockTitle = dock.windowTitle()
        log.debug("activate -> QDockWidget: %s" % dockTitle)
        if dockTitle in (u"Python Console", u"Console Python",  u"Message Window"):
            dock.setVisible(False)

    return True


def setSettings():
    """
    Stores the selected CFD code and updates action according with current
    selection and study states in the dekstop manager.
    """
    log.debug("setSettings")

    dsk = sgPyQt.getDesktop()
    ActionHandler = _DesktopMgr.getActionHandler(dsk)
    ActionHandler.updateActions()


def deactivate():
    """
    This method is called when GUI module is being deactivated.
    """
    log.debug("deactivate")
    dsk = sgPyQt.getDesktop()
    ActionHandler = _DesktopMgr.getActionHandler(dsk)
    ActionHandler.disconnect(ActionHandler._SalomeSelection, SIGNAL('currentSelectionChanged()'), ActionHandler.updateActions)
    ActionHandler.disconnectSolverGUI()


def createPopupMenu(popup, context):
    """
    This method is called when popup menu is requested by the user (right click).
    Should analyze the selection and fill in the popup menu with the corresponding actions.

    @type popup: C{QPopupMenu}
    @param popup: popup menu from the Object Browser.
    @type context: C{String}
    @param context: equal to 'ObjectBrowser' or 'VTKViewer' for example.
    """
    #log.debug("createPopupMenu -> context = %s" % context)

    study = CFDSTUDYGUI_DataModel._getStudy()
    dsk = sgPyQt.getDesktop()
    ActionHandler = _DesktopMgr.getActionHandler(dsk)

    #log.debug("createPopupMenu -> SelectedCount = %s" % sg.SelectedCount())

    if sg.SelectedCount() > 0:
        # Custom Popup menu added or removed regards to the type of the object
        for i in range(sg.SelectedCount()):
            entry = sg.getSelected(i)
            if entry != '':
                sobj = study.FindObjectID(entry)
                if sobj is not None:
                    test, anAttr = sobj.FindAttribute("AttributeLocalID")
                    if test:
                        id = anAttr._narrow(SALOMEDS.AttributeLocalID).Value()
                        if id >= 0:

                            if sobj.GetFatherComponent().GetName() == "Mesh":
                                if CFDSTUDYGUI_DataModel.getMeshFromMesh(sobj) == None:
                                    meshGroupObject,group = CFDSTUDYGUI_DataModel.getMeshFromGroup(sobj)
                                    if meshGroupObject != None:
                                        ActionHandler.customPopup(id, popup)
                                        if sg.SelectedCount() > 1:
                                            popup.removeAction(ActionHandler.commonAction(CFDSTUDYGUI_ActionsHandler.DisplayOnlyGroupMESHAction))
                                else:
                                    ActionHandler.customPopup(id, popup)
                                    popup.removeAction(ActionHandler.commonAction(CFDSTUDYGUI_ActionsHandler.DisplayOnlyGroupMESHAction))

                            else:
                                if not CFDSTUDYGUI_DataModel.isLinkPathObject(sobj):
                                    ActionHandler.customPopup(id, popup)
