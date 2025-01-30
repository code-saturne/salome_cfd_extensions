# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------------

# This file is part of Code_Saturne, a general-purpose CFD tool.
#
# Copyright (C) 1998-2025 EDF S.A.
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

"""
Actions Handler
===============

Creates menu, actions, and separators for the SALOME Desktop.
"""

# -------------------------------------------------------------------------------
# Standard modules
# -------------------------------------------------------------------------------

import os
import shutil
import subprocess
import re
import logging

# -------------------------------------------------------------------------------
# Third-party modules
# -------------------------------------------------------------------------------

from code_saturne.gui.base.QtCore import *
from code_saturne.gui.base.QtGui import *
from code_saturne.gui.base.QtWidgets import *
from code_saturne.gui.base import QtPage
from code_saturne.base.cs_exec_environment import enquote_arg

# -------------------------------------------------------------------------------
# Salome modules
# -------------------------------------------------------------------------------

import SALOMEDS  # Si on veut changer de couleur...
import salome
import SMESH
from salome.smesh import smeshBuilder

# -------------------------------------------------------------------------------
# Application modules
# -------------------------------------------------------------------------------

from . import CFDSTUDYGUI_DialogCollector
from . import CFDSTUDYGUI_DataModel
from . import CFDSTUDYGUI_Commons
from . import CFDSTUDYGUI_CommandMgr
# from CFDSTUDYGUI_Agents import *
from .CFDSTUDYGUI_DataModel import getCFDTW
from .CFDSTUDYGUI_Commons import _SetCFDCode, CFD_Code, BinCode, CFD_Saturne
from .CFDSTUDYGUI_Commons import CFD_Neptune, sgPyQt, sg, CheckCFD_CodeEnv
from . import CFDSTUDYGUI_SolverGUI
from .CFDSTUDYGUI_Message import cfdstudyMess
from .constants import col

# -------------------------------------------------------------------------------
# Global definitions
# -------------------------------------------------------------------------------

# Actions
SetStudyAction = 1
AddCaseAction = 2
LaunchGUIAction = 4
OpenGUIAction = 5
UpdateObjBrowserAction = 6
InfoCFDSTUDYAction = 7
OpenAnExistingCase = 8
UpdateCasePath = 9  # code_saturne create --import-only - popupmenu case

# common actions
RemoveAction = 20
ViewAction = 21
EditAction = 22
MoveToDRAFTAction = 23
CopyInDATAAction = 24
CopyInSRCAction = 25
CloseStudyAction = 27
DisplayImageAction = 28

# display action
ShowAction = 30
ShowOnlyAction = 31
HideAction = 32
FitAllAction = 33

# export/convert actions
ExportInParaViSAction = 40
ExportInSMESHAction = 41
ConvertMeshToMed = 42

# other actions
CheckCompilationAction = 50
RunScriptAction = 51

# Display Actions
DisplayMESHAction = 60
DisplayGroupMESHAction = 61
DisplayOnlyGroupMESHAction = 62
HideGroupMESHAction = 63
HideMESHAction = 64

DisplayTypeMenu = 70
DisplayTypePOINT = 71
DisplayTypeWIREFRAME = 72
DisplayTypeSHADED = 74
DisplayTypeINSIDEFRAME = 75
DisplayTypeSURFACEFRAME = 76
DisplayTypeFEATURE_EDGES = 77
DisplayTypeSHRINK = 78

# Syrthes Actions
OpenSyrthesCaseFile = 80
ExportSyrInSmesh = 81

# =====SOLVER ACTIONS
# Common Actions
SolverFileMenu = 100
SolverSaveAction = 101
SolverSaveAsAction = 102
SolverCloseAction = 103
SolverUndoAction = 104
SolverRedoAction = 105

SolverToolsMenu = 110
SolverOpenShellAction = 111
SolverDisplayCurrentCaseAction = 112

SolverEditSRCFiles = 121
SolverCompileSRCFiles = 122
SolverViewLogFiles = 123
SolverFileTransfer = 124

SolverLaunch = 131
SolverLaunchOT = 132

SolverHelpMenu = 140
SolverHelpAboutAction = 141

# Help menu
SolverHelpLicense = 251
SolverHelpGuidesMenu = 260
SolverHelpUserGuide = 261
SolverHelpTutorial = 262
SolverHelpTheory = 263
SolverHelpRefcard = 264
SolverHelpDoxygen = 265
NCSolverHelpUserGuide = 266
NCSolverHelpTutorial = 267
NCSolverHelpTheory = 268
NCSolverHelpDoxygen = 269

# ObjectTR is a convenient object for traduction purpose

ObjectTR = QObject()

# -------------------------------------------------------------------------------
# Classes definition
# -------------------------------------------------------------------------------


class ActionError(Exception):
    """
    New exception definition.
    """

    def __init__(self, value):
        """
        Constructor.
        """
        self.value = value

    def __str__(self):
        """
        String representation of the attribute I{self.value}.
        """
        return repr(self.value)


class CFDSTUDYGUI_ActionsHandler(QObject):
    def __init__(self):
        """
        Constructor.
        """
        logging.debug("__init__")
        QObject.__init__(self, None)

        from .clientgui import getClientGui
        self.getClientGui = getClientGui

        self.l_color = [(1, 0, 0), (0, 1, 0), (0, 0, 1),
                        (1, 1, 0), (1, 0, 1), (0, 1, 1),]
        self.ul_color = []
        # intialise all dialogs
        self.DialogCollector = CFDSTUDYGUI_DialogCollector.CFDSTUDYGUI_DialogCollector()

        self._ActionMap = {}
        self._CommonActionIdMap = {}
        self._SolverActionIdMap = {}
        self._HelpActionIdMap = {}

        self._SalomeSelection = sgPyQt.getSelection()
        self._SolverGUI = CFDSTUDYGUI_SolverGUI.CFDSTUDYGUI_SolverGUI()
        # self._DskAgent = Desktop_Agent()

        self.RemoveAction = RemoveAction
        self.DisplayImageAction = DisplayImageAction

        self.solverParentWidget = None
        self.selectedItem = None

    def getSolverGUI(self):
        return self._SolverGUI

    def setSolverParentWidget(self, solverParentWidget):
        """
        store the parent widget that will be used to embed solver GUI

        :param solverParentWidget: Qt widget that will be the parent of solver GUI widget
        :type solverParentWidget: QtWidget
        """
        logging.debug("set parent widget for solver GUI")
        self.solverParentWidget = solverParentWidget

    def createActions(self):
        """
        Creates menu, actions, and separators.
        """
        logging.debug("createActions")
        menu_id = sgPyQt.createMenu(ObjectTR.tr("CFDSTUDY_MENU"),
                                    -1,
                                    -1,
                                    10)
        tool_id = sgPyQt.createTool(ObjectTR.tr("CFDSTUDY_TOOL_BAR"))

        action = sgPyQt.createAction(-1,
                                     ObjectTR.tr("SET_CFDSTUDY_STUDY_TEXT"),
                                     ObjectTR.tr("SET_CFDSTUDY_STUDY_TIP"),
                                     ObjectTR.tr("SET_CFDSTUDY_STUDY_SB"),
                                     ObjectTR.tr("SET_CFDSTUDY_STUDY_ICON"))
        sgPyQt.createMenu(action, menu_id)
        sgPyQt.createTool(action, tool_id)

        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._CommonActionIdMap[SetStudyAction] = action_id
        action.triggered.connect(self.slotStudyLocation)

        action = sgPyQt.createSeparator()
        sgPyQt.createMenu(action, menu_id)
        sgPyQt.createTool(action, tool_id)

        action = sgPyQt.createAction(-1,
                                     ObjectTR.tr("ADD_CFDSTUDY_CASE_TEXT"),
                                     ObjectTR.tr("ADD_CFDSTUDY_CASE_TIP"),
                                     ObjectTR.tr("ADD_CFDSTUDY_CASE_SB"),
                                     ObjectTR.tr("ADD_CFDSTUDY_CASE_ICON"))
        sgPyQt.createTool(action, tool_id)
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._CommonActionIdMap[AddCaseAction] = action_id
        action.triggered.connect(self.slotAddCase)

        action = sgPyQt.createSeparator()
        sgPyQt.createMenu(action, menu_id)
        sgPyQt.createTool(action, tool_id)

        action = sgPyQt.createAction(-1,
                                     ObjectTR.tr("LAUNCH_CFDSTUDY_GUI_TEXT"),
                                     ObjectTR.tr("LAUNCH_CFDSTUDY_GUI_TIP"),
                                     ObjectTR.tr("LAUNCH_CFDSTUDY_GUI_SB"),
                                     ObjectTR.tr("LAUNCH_CFDSTUDY_GUI_ICON"))
        # popup open GUI on CFD CASE with slotLaunchGUI
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._CommonActionIdMap[LaunchGUIAction] = action_id
        action.triggered.connect(self.slotLaunchGUI)

        action = sgPyQt.createAction(-1,
                                     ObjectTR.tr("OPEN_CFDSTUDY_GUI_TEXT"),
                                     ObjectTR.tr("LAUNCH_CFDSTUDY_GUI_TIP"),
                                     ObjectTR.tr("LAUNCH_CFDSTUDY_GUI_SB"),
                                     ObjectTR.tr("LAUNCH_CFDSTUDY_GUI_ICON"))
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._CommonActionIdMap[OpenGUIAction] = action_id
        action.triggered.connect(self.slotOpenCFD_GUI)

        # Open An Existing Case with a Menu button
        action = sgPyQt.createAction(-1,
                                     ObjectTR.tr(
                                         "OPEN_EXISTING_CASE_GUI_TEXT"),
                                     ObjectTR.tr("OPEN_EXISTING_CASE_GUI_TIP"),
                                     ObjectTR.tr("OPEN_EXISTING_CASE_GUI_SB"),
                                     ObjectTR.tr("OPENEXISTINGCASEFILEXML_CFD_GUI_ACTION_ICON"))
        sgPyQt.createTool(action, tool_id)
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._CommonActionIdMap[OpenAnExistingCase] = action_id
        action.triggered.connect(self.slotOpenAnExistingCaseFileFromMenu)

        action = sgPyQt.createSeparator()
        sgPyQt.createMenu(action, menu_id)
        sgPyQt.createTool(action, tool_id)

        action = sgPyQt.createAction(-1,
                                     ObjectTR.tr(
                                         "UPDATE_CFDSTUDY_OBJBROWSER_TEXT"),
                                     ObjectTR.tr(
                                         "UPDATE_CFDSTUDY_OBJBROWSER_TIP"),
                                     ObjectTR.tr(
                                         "UPDATE_CFDSTUDY_OBJBROWSER_SB"),
                                     ObjectTR.tr("UPDATE_CFDSTUDY_OBJBROWSER_ICON"))
        sgPyQt.createMenu(action, menu_id)
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._CommonActionIdMap[UpdateObjBrowserAction] = action_id
        action.triggered.connect(self.slotUpdateObjectBrowser)

        action = sgPyQt.createSeparator()
        sgPyQt.createMenu(action, menu_id)

        action = sgPyQt.createAction(-1,
                                     ObjectTR.tr("INFO_CFDSTUDY_TEXT"),
                                     ObjectTR.tr("INFO_CFDSTUDY_TIP"),
                                     ObjectTR.tr("INFO_CFDSTUDY_SB"),
                                     ObjectTR.tr("INFO_CFDSTUDY_ICON"))

        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._CommonActionIdMap[InfoCFDSTUDYAction] = action_id
        action.triggered.connect(self.slotInfo)

        action = sgPyQt.createAction(-1,
                                     ObjectTR.tr("REMOVE_ACTION_TEXT"),
                                     ObjectTR.tr("REMOVE_ACTION_TIP"),
                                     ObjectTR.tr("REMOVE_ACTION_SB"),
                                     ObjectTR.tr("REMOVE_ACTION_ICON"))
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._CommonActionIdMap[RemoveAction] = action_id
        action.triggered.connect(self.slotRemoveAction)

        action = sgPyQt.createAction(-1,
                                     ObjectTR.tr("CLOSE_ACTION_TEXT"),
                                     ObjectTR.tr("CLOSE_ACTION_TIP"),
                                     ObjectTR.tr("CLOSE_ACTION_SB"),
                                     ObjectTR.tr("CLOSE_ACTION_ICON"))
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._CommonActionIdMap[CloseStudyAction] = action_id
        action.triggered.connect(self.slotCloseStudyAction)

        action = sgPyQt.createAction(-1,
                                     ObjectTR.tr("VIEW_ACTION_TEXT"),
                                     ObjectTR.tr("VIEW_ACTION_TIP"),
                                     ObjectTR.tr("VIEW_ACTION_SB"),
                                     ObjectTR.tr("VIEW_ACTION_ICON"))
        action.triggered.connect(self.slotViewAction)
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._CommonActionIdMap[ViewAction] = action_id

        action = sgPyQt.createAction(-1,
                                     ObjectTR.tr("EDIT_ACTION_TEXT"),
                                     ObjectTR.tr("EDIT_ACTION_TIP"),
                                     ObjectTR.tr("EDIT_ACTION_SB"),
                                     ObjectTR.tr("EDIT_ACTION_ICON"))
        action.triggered.connect(self.slotEditAction)
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._CommonActionIdMap[EditAction] = action_id

        action = sgPyQt.createAction(-1,
                                     ObjectTR.tr("DISPLAY_IMAGE_ACTION_TEXT"),
                                     ObjectTR.tr("DISPLAY_IMAGE_ACTION_TIP"),
                                     ObjectTR.tr("DISPLAY_IMAGE_ACTION_SB"),
                                     ObjectTR.tr("DISPLAY_IMAGE_ACTION_ICON"))
        action.triggered.connect(self.slotDisplayImageAction)
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._CommonActionIdMap[DisplayImageAction] = action_id

        action = sgPyQt.createAction(-1,
                                     ObjectTR.tr("MOVE_TO_DRAFT_ACTION_TEXT"),
                                     ObjectTR.tr("MOVE_TO_DRAFT_ACTION_TIP"),
                                     ObjectTR.tr("MOVE_TO_DRAFT_ACTION_SB"),
                                     ObjectTR.tr("MOVE_ACTION_ICON"))
        action.triggered.connect(self.slotMoveToDRAFT)
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._CommonActionIdMap[MoveToDRAFTAction] = action_id

        action = sgPyQt.createAction(-1,
                                     ObjectTR.tr("COPY_IN_DATA_ACTION_TEXT"),
                                     ObjectTR.tr("COPY_IN_DATA_ACTION_TIP"),
                                     ObjectTR.tr("COPY_IN_DATA_ACTION_SB"),
                                     ObjectTR.tr("COPY_ACTION_ICON"))
        action.triggered.connect(self.slotCopyInDATA)
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._CommonActionIdMap[CopyInDATAAction] = action_id

        action = sgPyQt.createAction(-1,
                                     ObjectTR.tr("COPY_IN_SRC_ACTION_TEXT"),
                                     ObjectTR.tr("COPY_IN_SRC_ACTION_TIP"),
                                     ObjectTR.tr("COPY_IN_SRC_ACTION_SB"),
                                     ObjectTR.tr("COPY_ACTION_ICON"))
        action.triggered.connect(self.slotCopyInSRC)
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._CommonActionIdMap[CopyInSRCAction] = action_id

        # export/convert actions
        action = sgPyQt.createAction(-1,
                                     ObjectTR.tr(
                                         "EXPORT_IN_PARAVIS_ACTION_TEXT"),
                                     ObjectTR.tr(
                                         "EXPORT_IN_PARAVIS_ACTION_TIP"),
                                     ObjectTR.tr(
                                         "EXPORT_IN_PARAVIS_ACTION_SB"),
                                     ObjectTR.tr("EXPORT_IN_PARAVIS_ACTION_ICON"))
        action.triggered.connect(self.slotExportInParavis)
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._CommonActionIdMap[ExportInParaViSAction] = action_id

        action = sgPyQt.createAction(-1,
                                     ObjectTR.tr(
                                         "EXPORT_IN_SMESH_ACTION_TEXT"),
                                     ObjectTR.tr("EXPORT_IN_SMESH_ACTION_TIP"),
                                     ObjectTR.tr("EXPORT_IN_SMESH_ACTION_SB"),
                                     ObjectTR.tr("EXPORT_IN_SMESH_ACTION_ICON"))
        action.triggered.connect(self.slotExportInSMESH)
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._CommonActionIdMap[ExportInSMESHAction] = action_id

        action = sgPyQt.createAction(-1,
                                     "Show",
                                     "Show the mesh or submesh in 3D View",
                                     "Show the mesh or submesh in 3D View",
                                     ObjectTR.tr("MESH_OBJ_ICON"))
        action.triggered.connect(self.slotShow)
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._CommonActionIdMap[ShowAction] = action_id

        action = sgPyQt.createAction(-1,
                                     "Show only",
                                     "Show only the mesh or submesh in 3D View",
                                     "Show only the mesh or submesh in 3D View",
                                     ObjectTR.tr("MESH_OBJ_ICON"))
        action.triggered.connect(self.slotShowOnly)
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._CommonActionIdMap[ShowOnlyAction] = action_id

        action = sgPyQt.createAction(-1,
                                     "Hide",
                                     "Hide the mesh or submesh in 3D View",
                                     "Hide the mesh or submesh in 3D View",
                                     ObjectTR.tr("MESH_OBJ_ICON"))
        action.triggered.connect(self.slotHide)
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._CommonActionIdMap[HideAction] = action_id

        action = sgPyQt.createAction(-1,
                                     "Fit all",
                                     "Fit all in 3D View",
                                     "Fit all in 3D View",
                                     ObjectTR.tr("MESH_OBJ_ICON"))
        action.triggered.connect(self.slotFitAll)
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._CommonActionIdMap[FitAllAction] = action_id

        action = sgPyQt.createAction(-1,
                                     ObjectTR.tr("ECS_CONVERT_ACTION_TEXT"),
                                     ObjectTR.tr("ECS_CONVERT_ACTION_TIP"),
                                     ObjectTR.tr("ECS_CONVERT_ACTION_SB"),
                                     ObjectTR.tr("ECS_CONVERT_ACTION_ICON"))
        action.triggered.connect(self.slotMeshConvertToMed)
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._CommonActionIdMap[ConvertMeshToMed] = action_id

        # popup added toupdate case path with code_saturne create --import-only
        # into case directory files
        action = sgPyQt.createAction(-1,
                                     ObjectTR.tr(
                                         "UPDATE_CASE_PATH_ACTION_TEXT"),
                                     ObjectTR.tr(
                                         "UPDATE_CASE_PATH_ACTION_TIP"),
                                     ObjectTR.tr("UPDATE_CASE_PATH_ACTION_SB"),
                                     ObjectTR.tr("UPDATE_CASE_PATH_ACTION_ICON"))
        action.triggered.connect(self.slotUpdateCasePath)
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._CommonActionIdMap[UpdateCasePath] = action_id

        # other actions
        action = sgPyQt.createAction(-1,
                                     ObjectTR.tr("RUN_SCRIPT_ACTION_TEXT"),
                                     ObjectTR.tr("RUN_SCRIPT_ACTION_TIP"),
                                     ObjectTR.tr("RUN_SCRIPT_ACTION_SB"),
                                     ObjectTR.tr("RUN_SCRIPT_ACTION_ICON"))
        action.triggered.connect(self.slotRunScript)
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._CommonActionIdMap[RunScriptAction] = action_id

        # syrthes actions
        action = sgPyQt.createAction(-1,
                                     ObjectTR.tr(
                                         "OPEN_SYRTHES-CASE_FILE_ACTION_TEXT"),
                                     ObjectTR.tr(
                                         "OPEN_SYRTHES-CASE_FILE_ACTION_TIP"),
                                     ObjectTR.tr(
                                         "OPEN_SYRTHES-CASE_FILE_ACTION_SB"),
                                     ObjectTR.tr("OPEN_SYRTHES-CASE_FILE_ACTION_ICON"))
        action.triggered.connect(self.slotOpenSyrthesCaseFile)
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._CommonActionIdMap[OpenSyrthesCaseFile] = action_id

        action = sgPyQt.createAction(-1,
                                     ObjectTR.tr(
                                         "EXPORT_SYR_FILE_ACTION_TEXT"),
                                     ObjectTR.tr("EXPORT_SYR_FILE_ACTION_TIP"),
                                     ObjectTR.tr("EXPORT_SYR_FILE_ACTION_SB"),
                                     ObjectTR.tr("EXPORT_IN_SMESH_ACTION_ICON"))
        action.triggered.connect(self.slotExportSyrInSmesh)
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._CommonActionIdMap[ExportSyrInSmesh] = action_id

        # Solver actions

        # File menu
        # find the menu File into the Main Menu Bar of Salome
        fileId = sgPyQt.createMenu(ObjectTR.tr("MEN_DESK_FILE"), -1, -1)

        # create my menu into  menu File at position 7
        action_id = sgPyQt.createMenu(ObjectTR.tr(
            "SOLVER_FILE_MENU_TEXT"), fileId, -1, 7, 1)
        self._SolverActionIdMap[SolverFileMenu] = action_id

        # warning: a Separator is a QMenu item (a trait)
        # create a separator after my menu in position 8
        action = sgPyQt.createSeparator()
        sgPyQt.createMenu(action, fileId, -1, 8, 1)

        # Save action
        action = sgPyQt.createAction(SolverSaveAction,
                                     ObjectTR.tr("SOLVER_SAVE_ACTION_TEXT"),
                                     ObjectTR.tr("SOLVER_SAVE_ACTION_TIP"),
                                     ObjectTR.tr("SOLVER_SAVE_ACTION_SB"),
                                     ObjectTR.tr("SOLVER_SAVE_ACTION_ICON"),
                                     Qt.SHIFT+Qt.CTRL+Qt.Key_S)
        sgPyQt.createTool(action, tool_id)
        sgPyQt.createMenu(action, self._SolverActionIdMap[SolverFileMenu], 100)
        action.triggered.connect(self.slotSaveDataFile)

        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._SolverActionIdMap[SolverSaveAction] = action_id

        # Save As action
        action = sgPyQt.createAction(-1,
                                     ObjectTR.tr("SOLVER_SAVEAS_ACTION_TEXT"),
                                     ObjectTR.tr("SOLVER_SAVEAS_ACTION_TIP"),
                                     ObjectTR.tr("SOLVER_SAVEAS_ACTION_SB"))
        sgPyQt.createMenu(action, self._SolverActionIdMap[SolverFileMenu], 100)
        action.triggered.connect(self.slotSaveAsDataFile)

        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._SolverActionIdMap[SolverSaveAsAction] = action_id
        action = sgPyQt.createSeparator()
        sgPyQt.createMenu(action, 1, 0, 2)

        # close GUI action
        action = sgPyQt.createAction(-1,
                                     ObjectTR.tr("CLOSE_CFD_GUI_ACTION_TEXT"),
                                     ObjectTR.tr("CLOSE_CFD_GUI_ACTION_TIP"),
                                     ObjectTR.tr("CLOSE_CFD_GUI_ACTION_SB"),
                                     ObjectTR.tr("CLOSE_CFD_GUI_ACTION_ICON"),
                                     Qt.SHIFT+Qt.CTRL+Qt.Key_W)
        sgPyQt.createTool(action, tool_id)
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._SolverActionIdMap[SolverCloseAction] = action_id
        action.triggered.connect(self.slotCloseCFD_GUI)

        # Add separator
        action = sgPyQt.createSeparator()
        sgPyQt.createTool(action, tool_id)

        # Undo action
        action = sgPyQt.createAction(-1, "Undo", "Undo", "Undo",
                                     ObjectTR.tr("UNDO_CFD_GUI_ACTION_ICON"))
        sgPyQt.createTool(action, tool_id)
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._SolverActionIdMap[SolverUndoAction] = action_id
        action.triggered.connect(self.slotUndo)

        # Redo action
        action = sgPyQt.createAction(-1, "Redo", "Redo", "Redo",
                                     ObjectTR.tr("REDO_CFD_GUI_ACTION_ICON"))
        sgPyQt.createTool(action, tool_id)
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._SolverActionIdMap[SolverRedoAction] = action_id
        action.triggered.connect(self.slotRedo)

        # Tools Menu
        action = sgPyQt.createSeparator()
        sgPyQt.createMenu(action, menu_id, 0, -1)

        action_id = sgPyQt.createMenu(
            ObjectTR.tr("SOLVER_TOOLS_MENU_TEXT"), menu_id)
        self._SolverActionIdMap[SolverToolsMenu] = action_id

        # Open shell action
        action = sgPyQt.createAction(-1,
                                     ObjectTR.tr(
                                         "SOLVER_OPENSHELL_ACTION_TEXT"),
                                     ObjectTR.tr(
                                         "SOLVER_OPENSHELL_ACTION_TIP"),
                                     ObjectTR.tr("SOLVER_OPENSHELL_ACTION_SB"))
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._SolverActionIdMap[SolverOpenShellAction] = action_id
        action.triggered.connect(self.slotOpenShell)

        sgPyQt.createMenu(action, self._SolverActionIdMap[SolverToolsMenu])

        action = sgPyQt.createSeparator()
        sgPyQt.createMenu(action, SolverToolsMenu, 0, -1)

        action = sgPyQt.createAction(-1,
                                     ObjectTR.tr(
                                         "SOLVER_DISPLAYCASE_ACTION_TEXT"),
                                     ObjectTR.tr(
                                         "SOLVER_DISPLAYCASE_ACTION_TIP"),
                                     ObjectTR.tr("SOLVER_DISPLAYCASE_ACTION_SB"))
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._SolverActionIdMap[SolverDisplayCurrentCaseAction] = action_id
        action.triggered.connect(self.slotDisplayCurrentCase)

        sgPyQt.createMenu(action, self._SolverActionIdMap[SolverToolsMenu])
        action = sgPyQt.createSeparator()
        sgPyQt.createMenu(action, SolverToolsMenu, 0, -1)

        # Management for User files (SRC, Logs, transfer to clusters)
        action = sgPyQt.createSeparator()
        sgPyQt.createMenu(action, menu_id)
        sgPyQt.createTool(action, tool_id)

        # SRC EDITOR
        action = sgPyQt.createAction(-1,
                                     ObjectTR.tr("SOLVER_EDITOR_ACTION_TEXT"),
                                     ObjectTR.tr("SOLVER_EDITOR_ACTION_TIP"),
                                     ObjectTR.tr("SOLVER_EDITOR_ACTION_SB"),
                                     ObjectTR.tr("CFDSTUDY_FILE_EDITOR_OBJ_ICON"))
        sgPyQt.createTool(action, tool_id)
        sgPyQt.createMenu(
            action, self._SolverActionIdMap[SolverToolsMenu], 100)
        action.triggered.connect(self.slotEditSRCFiles)

        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._SolverActionIdMap[SolverEditSRCFiles] = action_id

        # SRC COMPILER
        action = sgPyQt.createAction(-1,
                                     ObjectTR.tr(
                                         "SOLVER_COMPILER_ACTION_TEXT"),
                                     ObjectTR.tr("SOLVER_COMPILER_ACTION_TIP"),
                                     ObjectTR.tr("SOLVER_COMPILER_ACTION_SB"),
                                     ObjectTR.tr("CFDSTUDY_COMPILER_OBJ_ICON"))
        sgPyQt.createTool(action, tool_id)
        sgPyQt.createMenu(action, self._SolverActionIdMap[SolverToolsMenu])
        action.triggered.connect(self.slotCheckUsersCompilation)

        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._SolverActionIdMap[SolverCompileSRCFiles] = action_id

        # LOG VIEWER
        action = sgPyQt.createAction(-1,
                                     ObjectTR.tr(
                                         "SOLVER_LOGVIEWER_ACTION_TEXT"),
                                     ObjectTR.tr(
                                         "SOLVER_LOGVIEWER_ACTION_TIP"),
                                     ObjectTR.tr("SOLVER_LOGVIEWER_ACTION_SB"),
                                     ObjectTR.tr("CFDSTUDY_FILE_VIEWER_OBJ_ICON"))
        sgPyQt.createTool(action, tool_id)
        sgPyQt.createMenu(action, self._SolverActionIdMap[SolverToolsMenu])
        action.triggered.connect(self.slotViewLogFiles)

        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._SolverActionIdMap[SolverViewLogFiles] = action_id

        # FILE TRANSFER
        action = sgPyQt.createAction(-1,
                                     ObjectTR.tr(
                                         "SOLVER_FILETRANSFER_ACTION_TEXT"),
                                     ObjectTR.tr(
                                         "SOLVER_FILETRANSFER_ACTION_TIP"),
                                     ObjectTR.tr(
                                         "SOLVER_FILETRANSFER_ACTION_SB"),
                                     ObjectTR.tr("CFDSTUDY_FILE_TRANSFER_OBJ_ICON"))
        sgPyQt.createTool(action, tool_id)
        sgPyQt.createMenu(action, self._SolverActionIdMap[SolverToolsMenu])
        action.triggered.connect(self.slotFileTransfer)

        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._SolverActionIdMap[SolverFileTransfer] = action_id

        # Run computation
        action = sgPyQt.createAction(-1,
                                     ObjectTR.tr("SOLVER_LAUNCH_ACTION_TEXT"),
                                     ObjectTR.tr("SOLVER_LAUNCH_ACTION_TIP"),
                                     ObjectTR.tr("SOLVER_LAUNCH_ACTION_SB"),
                                     ObjectTR.tr("CFDSTUDY_SOLVER_LAUNCH_ICON"))
        sgPyQt.createTool(action, tool_id)
        sgPyQt.createMenu(action, self._SolverActionIdMap[SolverToolsMenu])
        action.triggered.connect(self.slotLaunchSolver)

        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._SolverActionIdMap[SolverLaunch] = action_id

        # OpenTURNS study
        action = sgPyQt.createAction(-1,
                                     ObjectTR.tr(
                                         "SOLVER_LAUNCH_OT_ACTION_TEXT"),
                                     ObjectTR.tr(
                                         "SOLVER_LAUNCH_OT_ACTION_TIP"),
                                     ObjectTR.tr("SOLVER_LAUNCH_OT_ACTION_SB"),
                                     ObjectTR.tr("CFDSTUDY_SOLVER_LAUNCH_OT_ICON"))
        sgPyQt.createTool(action, tool_id)
        sgPyQt.createMenu(action, self._SolverActionIdMap[SolverToolsMenu])
        action.triggered.connect(self.slotLaunchOT)

        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._SolverActionIdMap[SolverLaunchOT] = action_id

        # for auto hide last separator in tools menu
        self._HelpActionIdMap[0] = action_id

        # Help menu: insert a Solver Menu Help to the Main Menu Help of Salome

        helpId = sgPyQt.createMenu(ObjectTR.tr("MEN_DESK_HELP"), -1, -1)
        # Info: Separator created at the end of the Menu Help (when we did not indicate a number)

        action = sgPyQt.createSeparator()
        sgPyQt.createMenu(action, helpId)
        # Info: Solver Help Menu created at the end of the Menu Help of Salome(when we did not indicate a number)
        action_id = sgPyQt.createMenu("CFD module", helpId)
        self._SolverActionIdMap[SolverHelpMenu] = action_id

        m = "About CFD"
        action = sgPyQt.createAction(-1, m, m, m)
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._SolverActionIdMap[SolverHelpAboutAction] = action_id
        sgPyQt.createMenu(action, self._SolverActionIdMap[SolverHelpMenu])
        action.triggered.connect(self.slotHelpAbout)
        self._ActionMap[action_id].setVisible(True)

        m = "License"
        action = sgPyQt.createAction(SolverHelpLicense, m, m, m)
        sgPyQt.createMenu(action, self._SolverActionIdMap[SolverHelpMenu])
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._HelpActionIdMap[SolverHelpLicense] = action_id
        action.triggered.connect(self.slotHelpLicense)

        # Guides menu
        action_id = sgPyQt.createMenu(
            "Code_Saturne and NEPTUNE_CFD Guides", self._SolverActionIdMap[SolverHelpMenu])
        self._HelpActionIdMap[SolverHelpGuidesMenu] = action_id

        m = "Code_Saturne user guide"
        action = sgPyQt.createAction(SolverHelpUserGuide, m, m, m)
        sgPyQt.createMenu(action, self._HelpActionIdMap[SolverHelpGuidesMenu])
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._HelpActionIdMap[SolverHelpUserGuide] = action_id
        action.triggered.connect(self.slotHelpUserGuide)

        m = "Code_Saturne tutorial"
        action = sgPyQt.createAction(SolverHelpTutorial, m, m, m)
        sgPyQt.createMenu(action, self._HelpActionIdMap[SolverHelpGuidesMenu])
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._HelpActionIdMap[SolverHelpTutorial] = action_id
        action.triggered.connect(self.slotHelpTutorial)

        m = "Code_Saturne theoretical guide"
        action = sgPyQt.createAction(SolverHelpTheory, m, m, m)
        sgPyQt.createMenu(action, self._HelpActionIdMap[SolverHelpGuidesMenu])
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._HelpActionIdMap[SolverHelpTheory] = action_id
        action.triggered.connect(self.slotHelpTheory)

        m = "Reference card"
        action = sgPyQt.createAction(SolverHelpRefcard, m, m, m)
        sgPyQt.createMenu(action, self._HelpActionIdMap[SolverHelpGuidesMenu])
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._HelpActionIdMap[SolverHelpRefcard] = action_id
        action.triggered.connect(self.slotHelpRefcard)

        m = "Code_Saturne doxygen"
        action = sgPyQt.createAction(SolverHelpDoxygen, m, m, m)
        sgPyQt.createMenu(action, self._HelpActionIdMap[SolverHelpGuidesMenu])
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._HelpActionIdMap[SolverHelpDoxygen] = action_id
        action.triggered.connect(self.slotHelpDoxygen)

        m = "NEPTUNE_CFD user guide"
        action = sgPyQt.createAction(NCSolverHelpUserGuide, m, m, m)
        sgPyQt.createMenu(action, self._HelpActionIdMap[SolverHelpGuidesMenu])
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._HelpActionIdMap[NCSolverHelpUserGuide] = action_id
        action.triggered.connect(self.slotHelpNCUserGuide)

        m = "NEPTUNE_CFD tutorial"
        action = sgPyQt.createAction(NCSolverHelpTutorial, m, m, m)
        sgPyQt.createMenu(action, self._HelpActionIdMap[SolverHelpGuidesMenu])
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._HelpActionIdMap[NCSolverHelpTutorial] = action_id
        action.triggered.connect(self.slotHelpNCTutorial)

        m = "NEPTUNE_CFD theoretical guide"
        action = sgPyQt.createAction(NCSolverHelpTheory, m, m, m)
        sgPyQt.createMenu(action, self._HelpActionIdMap[SolverHelpGuidesMenu])
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._HelpActionIdMap[NCSolverHelpTheory] = action_id
        action.triggered.connect(self.slotHelpNCTheory)

        m = "NEPTUNE_CFD doxygen"
        action = sgPyQt.createAction(NCSolverHelpDoxygen, m, m, m)
        sgPyQt.createMenu(action, self._HelpActionIdMap[SolverHelpGuidesMenu])
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._HelpActionIdMap[NCSolverHelpDoxygen] = action_id
        action.triggered.connect(self.slotHelpNCDoxygen)

        self.updateActions()

    def findStudyItem(self, twItem):
        """
        retrieve the study item
        """
        cur = twItem
        while cur:
            if cur.text(col.id) == str(CFDSTUDYGUI_DataModel.dict_object["Study"]):
                return cur
            cur = cur.parent()
        logging.debug("************* outside Study ? *****************")
        return None

    def findCaseItem(self, twItem):
        """
        retrieve the case item
        """
        cur = twItem
        while cur:
            if cur.text(col.id) == str(CFDSTUDYGUI_DataModel.dict_object["Case"]):
                return cur
            cur = cur.parent()
        logging.debug("************* outside Study ? *****************")
        return None

    def updateActions(self):
        """
        Updates all action according with current selection and study states.
        This function connected to selection change signal.
        """
        logging.debug("updateActions")

        # enable all actions
        for i in self._CommonActionIdMap:
            if not i == InfoCFDSTUDYAction:
                self.commonAction(i).setEnabled(True)

        items = self.getClientGui().getTWSelectedItems()

        if len(items) != 1:
            logging.debug("no selection or multiple selection")
            for i in self._CommonActionIdMap:
                if i != InfoCFDSTUDYAction:
                    if i == SetStudyAction or i == OpenAnExistingCase:
                        self.commonAction(i).setEnabled(True)
                    else:
                        # multiple selection not authorized
                        self.commonAction(i).setEnabled(False)

        if len(items) == 1:
            item = items[0]
            self.selectedItem = item
            id = item.text(col.id)
            logging.debug("single selection %s", id)
            isStudy = (id == str(CFDSTUDYGUI_DataModel.dict_object["Study"]))
            self.commonAction(AddCaseAction).setEnabled(isStudy)
            aStudy = self.findStudyItem(item)
            aCase = self.findCaseItem(item)

            if aCase != None:
                logging.debug("aCase != None")
                # code = CFDSTUDYGUI_DataModel.checkCode(aCase)
                code = "Code_Saturne"  # TODO: rewrite a check for "Code_Saturne" or "NEPTUNE_CFD"
                _SetCFDCode(code)
                dialog = self.DialogCollector.InfoDialog
                dialog.update(code)

            if aStudy != None and aCase != None:
                logging.debug("aStudy != None and aCase != None")
                boo = (id == str(CFDSTUDYGUI_DataModel.dict_object["DATALaunch"])) or \
                      (id == str(CFDSTUDYGUI_DataModel.dict_object["Case"]))
                self.commonAction(LaunchGUIAction).setEnabled(boo)
                self.solverAction(SolverCloseAction).setEnabled(True)
                # self.commonAction(OpenGUIAction).setEnabled(CFDSTUDYGUI_DataModel.checkCaseLaunchGUI(aCase))
                self.commonAction(OpenGUIAction).setEnabled(
                    True)  # TODO: check
            else:
                self.commonAction(LaunchGUIAction).setEnabled(False)
        else:
            self.commonAction(AddCaseAction).setEnabled(False)
        # enable / disable solver actions
        isActivatedView = self._SolverGUI.isActive()  # Main GUI Window is active
        logging.debug("isActivatedView: %s", isActivatedView)

        for a in self._SolverActionIdMap:
            if a != SolverFileMenu and a != SolverToolsMenu and a != SolverHelpMenu:
                logging.debug("setEnabled(%s) %s", isActivatedView, a)
                self.solverAction(a).setEnabled(isActivatedView)

        from code_saturne.base.cs_package import package
        pkg = package(name='neptune_cfd')
        bin_ncfd = os.path.join(pkg.get_dir('bindir'),
                                'neptune_cfd'+pkg.config.shext)

        if not os.path.isfile(bin_ncfd):
            self.solverAction(NCSolverHelpUserGuide).setEnabled(False)
            self.solverAction(NCSolverHelpTutorial).setEnabled(False)
            self.solverAction(NCSolverHelpTheory).setEnabled(False)
            self.solverAction(NCSolverHelpDoxygen).setEnabled(False)

        if len(items) == 1:
            item = items[0]
            self.updateActionsXmlFileItem(item)
            if (id == str(CFDSTUDYGUI_DataModel.dict_object["Case"])):
                idParent = item.parent().text(col.id)
                if (idParent == str(CFDSTUDYGUI_DataModel.dict_object["CouplingStudy"])):
                    self.commonAction(RemoveAction).setEnabled(False)
                    self.commonAction(RemoveAction).setVisible(False)
                if (idParent == str(CFDSTUDYGUI_DataModel.dict_object["Study"])):
                    self.commonAction(RemoveAction).setEnabled(True)
                    self.commonAction(RemoveAction).setVisible(True)
            if (id == str(CFDSTUDYGUI_DataModel.dict_object["RESUSubFolder"])):
                self.commonAction(RemoveAction).setVisible(True)
            if (id == str(CFDSTUDYGUI_DataModel.dict_object["RESUSubErrFolder"])):
                self.commonAction(RemoveAction).setVisible(True)
            if (id == str(CFDSTUDYGUI_DataModel.dict_object["RESU_COUPLINGSubFolder"])):
                self.commonAction(RemoveAction).setVisible(True)

        for act in (ShowAction, ShowOnlyAction, HideAction, FitAllAction):
            self.commonAction(act).setVisible(True)

    def updateActionsXmlFileItem(self, item):
        id = item.text(col.id)
        logging.debug("updateActionsXmlFile %s", id)
        isStudy = (id == str(CFDSTUDYGUI_DataModel.dict_object["Study"]))
        self.commonAction(AddCaseAction).setEnabled(isStudy)
        study = self.findStudyItem(item)
        case = self.findCaseItem(item)
        if (id == str(CFDSTUDYGUI_DataModel.dict_object["DATAfileXML"])):
            self.solverAction(SolverCloseAction).setEnabled(False)
            self.solverAction(SolverSaveAction).setEnabled(False)
            self.solverAction(SolverSaveAsAction).setEnabled(False)
            self.solverAction(SolverUndoAction).setEnabled(False)
            self.solverAction(SolverRedoAction).setEnabled(False)
            if case != None and study != None:
                self.solverAction(SolverCloseAction).setEnabled(True)
                self.commonAction(OpenGUIAction).setEnabled(False)
                self.solverAction(SolverSaveAction).setEnabled(True)
                self.solverAction(SolverSaveAsAction).setEnabled(True)
                self.solverAction(SolverUndoAction).setEnabled(True)
                self.solverAction(SolverRedoAction).setEnabled(True)

    def updateActionsXmlFile(self, XMLSobj):
        logging.debug("updateActionsXmlFile")
        # TODO : rewrite if useful ?
        # if XMLSobj != None:
        #     if CFDSTUDYGUI_DataModel.checkType(XMLSobj,
        #                                        CFDSTUDYGUI_DataModel.dict_object["DATAfileXML"]):
        #         self.solverAction(SolverCloseAction).setEnabled(False)
        #         self.solverAction(SolverSaveAction).setEnabled(False)
        #         self.solverAction(SolverSaveAsAction).setEnabled(False)
        #         self.solverAction(SolverUndoAction).setEnabled(False)
        #         self.solverAction(SolverRedoAction).setEnabled(False)

        #         case   = CFDSTUDYGUI_DataModel.GetCase(XMLSobj)
        #         study  = CFDSTUDYGUI_DataModel.GetStudyByObj(XMLSobj)
        #         if case != None and study != None:

        #             if CFDSTUDYGUI_SolverGUI._c_CFDGUI.findDock(XMLSobj.GetName(),
        #                                                         case.GetName(),
        #                                                         study.GetName()):
        #                 self.solverAction(SolverCloseAction).setEnabled(True)
        #                 self.commonAction(OpenGUIAction).setEnabled(False)
        #                 self.solverAction(SolverSaveAction).setEnabled(True)
        #                 self.solverAction(SolverSaveAsAction).setEnabled(True)
        #                 self.solverAction(SolverUndoAction).setEnabled(True)
        #                 self.solverAction(SolverRedoAction).setEnabled(True)

    def customPopup(self, item, popup):
        """
        Callback for fill popup menu according current selection state.
        Function called by C{createPopupMenu} from CFDSTUDYGUI.py

        @type id: C{int}
        @param id: type of the branch tree slected in the Object Brower.
        @type popup: C{QPopupMenu}
        @param popup: popup menu from the Object Browser.
        """
        self.selectedItem = item
        idText = item.text(col.id)
        id = 0
        if idText:
            id = int(idText)
        logging.debug("customPopup %s", id)
        if id == CFDSTUDYGUI_DataModel.dict_object["Study"]:
            popup.addAction(self.commonAction(AddCaseAction))
            popup.addAction(self.commonAction(CloseStudyAction))
            popup.addAction(self.commonAction(UpdateObjBrowserAction))
        if id == CFDSTUDYGUI_DataModel.dict_object["CouplingStudy"]:
            popup.addAction(self.commonAction(CloseStudyAction))
            popup.addAction(self.commonAction(UpdateObjBrowserAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["Case"]:
            popup.addAction(self.commonAction(LaunchGUIAction))
            popup.addAction(self.solverAction(SolverCloseAction))
            popup.addAction(self.commonAction(UpdateCasePath))
            popup.addAction(self.commonAction(RemoveAction))
            popup.addAction(self.commonAction(UpdateObjBrowserAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["DATAFolder"] or \
                id == CFDSTUDYGUI_DataModel.dict_object["REFERENCEDATAFolder"] or \
                id == CFDSTUDYGUI_DataModel.dict_object["DRAFTFolder"] or \
                id == CFDSTUDYGUI_DataModel.dict_object["SRCFolder"] or \
                id == CFDSTUDYGUI_DataModel.dict_object["USERSFolder"] or \
                id == CFDSTUDYGUI_DataModel.dict_object["RESUFolder"] or \
                id == CFDSTUDYGUI_DataModel.dict_object["RESU_COUPLINGFolder"] or \
                id == CFDSTUDYGUI_DataModel.dict_object["RESSRCFolder"] or \
                id == CFDSTUDYGUI_DataModel.dict_object["HISTFolder"] or \
                id == CFDSTUDYGUI_DataModel.dict_object["PRETFolder"] or \
                id == CFDSTUDYGUI_DataModel.dict_object["SUITEFolder"] or \
                id == CFDSTUDYGUI_DataModel.dict_object["POSTPROFolder"] or \
                id == CFDSTUDYGUI_DataModel.dict_object["MESHFolder"] or \
                id == CFDSTUDYGUI_DataModel.dict_object["POSTFolder"]:
            popup.addAction(self.commonAction(UpdateObjBrowserAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["DATARunConf"]:
            popup.addAction(self.commonAction(ViewAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["DATAFile"]:
            popup.addAction(self.commonAction(EditAction))
            popup.addAction(self.commonAction(MoveToDRAFTAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["DATAPyFile"]:
            popup.addAction(self.commonAction(EditAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["DATADRAFTFile"]:
            popup.addAction(self.commonAction(EditAction))
            popup.addAction(self.commonAction(RemoveAction))
            popup.addAction(self.commonAction(CopyInDATAAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["REFERENCEDATAFile"]:
            popup.addAction(self.commonAction(ViewAction))
            popup.addAction(self.commonAction(CopyInDATAAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["DATALaunch"]:
            popup.addAction(self.commonAction(LaunchGUIAction))
            popup.addAction(self.commonAction(RunScriptAction))
            popup.addAction(self.commonAction(ViewAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["DATAfileXML"]:
            popup.addAction(self.commonAction(OpenGUIAction))
            popup.addAction(self.solverAction(SolverCloseAction))
            popup.addAction(self.commonAction(InfoCFDSTUDYAction))
        # elif id == CFDSTUDYGUI_DataModel.dict_object["SRCFolder"]:
        #     popup.addAction(self.commonAction(CheckCompilationAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["SRCFile"]:
            # popup.addAction(self.commonAction(CheckCompilationAction))
            popup.addAction(self.commonAction(EditAction))
            popup.addAction(self.commonAction(MoveToDRAFTAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["SRCDRAFTFile"]:
            popup.addAction(self.commonAction(EditAction))
            popup.addAction(self.commonAction(RemoveAction))
            popup.addAction(self.commonAction(CopyInSRCAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["LOGSRCFile"]:
            popup.addAction(self.commonAction(ViewAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["USRSRCFile"]:
            popup.addAction(self.commonAction(ViewAction))
            popup.addAction(self.commonAction(CopyInSRCAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["RESUFile"]:
            popup.addAction(self.commonAction(ViewAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["RESUSubFolder"]:
            popup.addAction(self.commonAction(RemoveAction))
            popup.addAction(self.commonAction(UpdateObjBrowserAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["RESUSubErrFolder"]:
            popup.addAction(self.commonAction(RemoveAction))
            popup.addAction(self.commonAction(UpdateObjBrowserAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["RESU_COUPLINGSubFolder"]:
            popup.addAction(self.commonAction(RemoveAction))
            popup.addAction(self.commonAction(UpdateObjBrowserAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["RESSRCFile"]:
            popup.addAction(self.commonAction(ViewAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["HISTFile"]:
            popup.addAction(self.commonAction(ViewAction))
            # popup.addAction(self.commonAction(ExportInParaViSAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["RESMEDFile"] \
                or id == CFDSTUDYGUI_DataModel.dict_object["RESENSIGHTFile"]:
            # popup.addAction(self.commonAction(ExportInParaViSAction))
            pass
        elif id == CFDSTUDYGUI_DataModel.dict_object["DESFile"] \
                or id == CFDSTUDYGUI_DataModel.dict_object["CGNSFile"] \
                or id == CFDSTUDYGUI_DataModel.dict_object["CcmFile"] \
                or id == CFDSTUDYGUI_DataModel.dict_object["CaseFile"] \
                or id == CFDSTUDYGUI_DataModel.dict_object["NeuFile"] \
                or id == CFDSTUDYGUI_DataModel.dict_object["MSHFile"] \
                or id == CFDSTUDYGUI_DataModel.dict_object["HexFile"] \
                or id == CFDSTUDYGUI_DataModel.dict_object["UnvFile"]:
            popup.addAction(self.commonAction(ConvertMeshToMed))
        elif id == CFDSTUDYGUI_DataModel.dict_object["MEDFile"]:
            popup.addAction(self.commonAction(ExportInSMESHAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["MESHFile"]:
            popup.addAction(self.commonAction(ViewAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["DATFile"]:
            popup.addAction(self.commonAction(EditAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["RESUPNGFile"]:
            popup.addAction(self.commonAction(DisplayImageAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["POSTFile"]:
            popup.addAction(self.commonAction(ViewAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["SyrthesFile"]:
            popup.addAction(self.commonAction(ViewAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["SyrthesSydFile"]:
            popup.addAction(self.commonAction(ViewAction))
            popup.addAction(self.commonAction(OpenSyrthesCaseFile))
        elif id == CFDSTUDYGUI_DataModel.dict_object["SYRMESHFile"]:
            popup.addAction(self.commonAction(ExportSyrInSmesh))
        elif id == CFDSTUDYGUI_DataModel.dict_object["CouplingFilePy"]:
            popup.addAction(self.commonAction(EditAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["CouplingLauncher"]:
            popup.addAction(self.commonAction(EditAction))
            popup.addAction(self.commonAction(RunScriptAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["USRSRCSYRFile"]:
            popup.addAction(self.commonAction(EditAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["SYRCaseFolder"]:
            popup.addAction(self.commonAction(UpdateObjBrowserAction))
        elif id == "VTKViewer":
            popup.addAction(self.commonAction(DisplayTypeSHADED))
            popup.addAction(self.commonAction(DisplayTypeWIREFRAME))

        if id == id == CFDSTUDYGUI_DataModel.dict_object["MEDFile"] \
                or id == CFDSTUDYGUI_DataModel.dict_object["Display"]:
            popup.addAction(self.commonAction(ShowAction))
            popup.addAction(self.commonAction(ShowOnlyAction))
            popup.addAction(self.commonAction(HideAction))
            popup.addAction(self.commonAction(FitAllAction))

    def slotStudyLocation(self):
        """
        Loads the CFD study location. If the name of the CFD study
        does not exist, the corresponding folder is created.
        dialog.CreateOption boolean indicates that Create study button is checked
        """
        logging.debug("slotStudyLocation")
        dialog = self.DialogCollector.SetTreeLocationDialog
        dialog.__init__()
        dialog.exec_()
        if self.DialogCollector.SetTreeLocationDialog.result() == QDialog.Accepted:
            cursor = QCursor(Qt.BusyCursor)
            QApplication.setOverrideCursor(cursor)
            iok = True
            _SetCFDCode(dialog.code)
            if os.path.exists(dialog.StudyPath):
                boo = CFDSTUDYGUI_Commons.isaCFDCase(dialog.StudyPath)
                if boo:
                    iok = getCFDTW()._SetCaseLocation(dialog.StudyPath)
                else:
                    iok = getCFDTW()._SetStudyLocation(theStudyPath=dialog.StudyPath,
                                                       theCaseName=dialog.CaseNames,
                                                       theCreateOpt=dialog.CreateOption,
                                                       theCopyOpt=dialog.CopyFromOption,
                                                       theNameRef=dialog.CaseRefName,
                                                       theSyrthesOpt=dialog.CouplingSaturneSyrthes,
                                                       theSyrthesCase=dialog.SyrthesCase,
                                                       theNprocs=dialog.Nprocs)
            else:
                iok = getCFDTW()._SetStudyLocation(theStudyPath=dialog.StudyPath,
                                                   theCaseName=dialog.CaseNames,
                                                   theCreateOpt=dialog.CreateOption,
                                                   theCopyOpt=dialog.CopyFromOption,
                                                   theNameRef=dialog.CaseRefName,
                                                   theSyrthesOpt=dialog.CouplingSaturneSyrthes,
                                                   theSyrthesCase=dialog.SyrthesCase,
                                                   theNprocs=dialog.Nprocs)
            if iok:
                sg.updateObjBrowser()
                self.updateActions()
            QApplication.restoreOverrideCursor()

    def slotAddCase(self):
        """
        Builds new CFD cases.
        """
        entry = self.selectedItem.text(col.entry)
        logging.debug("slotAddCase %s", entry)
        dialog = self.DialogCollector.SetTreeLocationDialog
        dialog.__init__()
        dialog.setCaseMode()

        studyTwi = getCFDTW().entryToTwi[entry]
        studyObj = getCFDTW().getObjFromEntry(entry)
        studyPath = studyTwi.text(col.details)
        dialog.StudyPath = studyPath
        dialog.StudyDirName.setText(os.path.dirname(studyPath))
        dialog.StudyLineEdit.setText(os.path.basename(studyPath))
        if not os.path.exists(dialog.StudyPath):
            mess = cfdstudyMess.trMessage(self.tr("ENV_DLG_INVALID_DIRECTORY"), [
                                          dialog.StudyPath])+self.tr("STMSG_UPDATE_STUDY_INCOMING")
            cfdstudyMess.aboutMessage(mess)
            getCFDTW().UpdateSubTree(studyTwi)
            return
        dialog.exec_()
        if self.DialogCollector.SetTreeLocationDialog.result() != QDialog.Accepted:
            # --- reinitialization
            dialog.setCaseMode()
            return
        _SetCFDCode(dialog.code)
        # --- Get existing case name list of a CFD study
        ExistingCaseNameList = getCFDTW().GetCaseNameList(studyTwi)
        logging.debug("ExistingCaseNameList %s", ExistingCaseNameList)
        if dialog.CaseNames != "":
            newCaseList = str(dialog.CaseNames).strip().split()
            logging.debug("newCaseList %s", newCaseList)
            for i in newCaseList:
                if i in ExistingCaseNameList:
                    mess = cfdstudyMess.trMessage(
                        self.tr("CASE_ALREADY_EXISTS"), [i, studyPath])
                    cfdstudyMess.aboutMessage(mess)
                else:
                    iok = getCFDTW()._SetStudyLocation(theStudyPath=dialog.StudyPath,
                                                       theCaseName=i,
                                                       theCreateOpt=dialog.CreateOption,
                                                       theCopyOpt=dialog.CopyFromOption,
                                                       theNameRef=dialog.CaseRefName,
                                                       theSyrthesOpt=False,
                                                       theSyrthesCase="",
                                                       theNprocs="")
        if str(dialog.CaseNames).strip() == "":
            if "CASE1" in ExistingCaseNameList:
                mess = cfdstudyMess.trMessage(self.tr("DEFAULT_CASE_ALREADY_EXISTS"), [
                                              "CASE1", CFDSTUDYGUI_DataModel._GetPath(studyObj)])
                cfdstudyMess.aboutMessage(mess)
            else:
                iok = getCFDTW()._SetStudyLocation(theStudyPath=dialog.StudyPath,
                                                   theCaseName="CASE1",
                                                   theCreateOpt=dialog.CreateOption,
                                                   theCopyOpt=dialog.CopyFromOption,
                                                   theNameRef=dialog.CaseRefName,
                                                   theSyrthesOpt=False,
                                                   theSyrthesCase="",
                                                   theNprocs="")
        getCFDTW().rebuildTWRecursively(studyTwi)
        getCFDTW().UpdateSubTree(studyTwi)

    def slotInfo(self):
        """
        Shows the QDialog with the info from CFDSTUDY:
            - CFD code selected
            - environnement variables defined
        """
        logging.debug("slotInfo")
        dialog = self.DialogCollector.InfoDialog
        dialog.show()
        self.updateActions()

    def slotUpdateObjectBrowser(self):
        """
        Re-reads the unix folders and updates the complete representation
        of the CFD studies in the Object Browser.
        """
        logging.debug("slotUpdateObjectBrowser")
        twi = self.selectedItem
        if twi:
            getCFDTW().UpdateSubTree(twi)
        else:
            getCFDTW().UpdateSubTree()

    def updateObjBrowser(self, Object=None):
        """
        Updates CFD study sub-tree from the argument object.

        @type theObject: C{SObject}
        @param theObject: branch of a tree of data to update.
        """
        logging.debug("updateObjBrowser")
        cursor = QCursor(Qt.BusyCursor)
        QApplication.setOverrideCursor(cursor)

        if Object:
            twi = getCFDTW().entryToTwi[Object.GetID()]
            getCFDTW().UpdateSubTree(twi)

        QApplication.restoreOverrideCursor()

    def slotViewAction(self):
        """
        Edits in the read only mode the file selected in the Object Browser.
        Warning, the editor is always emacs!
        """
        logging.debug("slotViewAction")
        viewerName = str(sgPyQt.stringSetting(
            "CFDSTUDY", "ExternalReader", str(self.tr("CFDSTUDY_PREF_READER")))).strip()
        if viewerName != "":
            if self.selectedItem is not None:
                path = self.selectedItem.text(col.details)
                try:
                    if re.match(".*emacs$", viewerName):
                        subprocess.Popen(
                            [viewerName, path, "-f", "toggle-read-only"])
                    elif re.match("vi", viewerName) or re.match("vim", viewerName):
                        subprocess.Popen("xterm -sb -e vi " + path, shell=True)
                    elif viewerName == "gvim":
                        subprocess.Popen([viewerName, path, "-R"])
                    else:
                        subprocess.Popen([viewerName, path])
                except:
                    mess = cfdstudyMess.trMessage(self.tr("VERIFY_VIEWER_NAME_PREFERENCE"), [
                                                  str(self.tr("EXTERNAL_READER"))])
                    cfdstudyMess.aboutMessage(mess)
        else:
            mess = cfdstudyMess.trMessage(self.tr("ADD_VIEWER_NAME_PREFERENCE"), [
                                          str(self.tr("EXTERNAL_READER"))])
            cfdstudyMess.aboutMessage(mess)

    def slotEditAction(self):
        """
        Edits in the user's editor the file selected in the Object Browser.
        """
        logging.debug("slotEditAction")
        viewerName = str(sgPyQt.stringSetting(
            "CFDSTUDY", "ExternalEditor", str(self.tr("CFDSTUDY_PREF_EDITOR")))).strip()
        if str(viewerName) != "":
            if self.selectedItem is not None:
                path = self.selectedItem.text(col.details)
                try:
                    subprocess.Popen([viewerName, path])
                except:
                    mess = cfdstudyMess.trMessage(self.tr("VERIFY_EDITOR_NAME_PREFERENCE"), [
                                                  str(self.tr("EXTERNAL_EDITOR"))])
                    cfdstudyMess.aboutMessage(mess)
        else:
            mess = cfdstudyMess.trMessage(self.tr("ADD_VIEWER_NAME_PREFERENCE"), [
                                          str(self.tr("EXTERNAL_EDITOR"))])
            cfdstudyMess.aboutMessage(mess)

    def slotDisplayImageAction(self):
        """
        Edits in the read only mode the file selected in the Object Browser.
        Warning, the editor is always emacs!
        """
        logging.debug("slotDisplayImageAction")
        displayViewerName = str(sgPyQt.stringSetting("CFDSTUDY", "ExternalDisplay", str(
            self.tr("CFDSTUDY_PREF_DISPLAY_VIEWER")))).strip()
        if displayViewerName != "":

            listSobj = self._multipleSelectedObject()
            if listSobj != []:
                for sobj in listSobj:
                    path = CFDSTUDYGUI_DataModel._GetPath(sobj)
                    try:
                        if re.match("display", displayViewerName) or re.match("eog", displayViewerName):
                            subprocess.Popen([displayViewerName, path])
                        else:
                            subprocess.Popen([displayViewerName, path])
                    except:
                        mess = cfdstudyMess.trMessage(self.tr("VERIFY_DISPLAY_VIEWER_NAME_PREFERENCE"), [
                                                      str(self.tr("EXTERNAL_DISPLAY"))])
                        cfdstudyMess.aboutMessage(mess)
        else:
            mess = cfdstudyMess.trMessage(self.tr("ADD_DISPLAY_VIEWER_NAME_PREFERENCE"), [
                                          str(self.tr("EXTERNAL_DISPLAY"))])
            cfdstudyMess.aboutMessage(mess)

    def slotCloseStudyAction(self):
        """
        Close file or folder and children from the Object Browser.
        Delete dock windows cases attached to a CFD Study if this study is being closed from the Object Browser.
        """
        logging.debug("slotCloseStudyAction")
        studyTwi = self.selectedItem
        caseList = []
        if studyTwi:
            theStudypath = studyTwi.text(col.details)
            mess = cfdstudyMess.trMessage(
                self.tr("CLOSE_ACTION_CONFIRM_MESS"), [theStudypath])
            if cfdstudyMess.warningMessage(mess) == QMessageBox.No:
                return
            theStudy = getCFDTW().getObjFromTwi(studyTwi)
            caseList = getCFDTW().GetCaseList(studyTwi)
            if caseList != []:
                for aCase in caseList:
                    self.CloseCFD_GUI(aCase)
            getCFDTW().removeObjFromTwi(studyTwi)
            getCFDTW().removeTwiWithChildren(studyTwi)

    def slotRemoveAction(self):
        logging.debug("slotRemoveAction")
        if self.selectedItem is not None:
            self.removeAction_obj(self.selectedItem)

    def removeAction_obj(self, twItem):
        """
        Deletes file or folder from the Object Browser, and from the unix system files.
        Delete dock windows attached to a CFD Study if this study is deleted from the Object Browser.
        """
        itemPath = twItem.text(col.details)
        itemId = 0
        itemTextId = twItem.text(col.id)
        if itemTextId:
            itemId = int(itemTextId)
        if itemPath:
            if itemId == CFDSTUDYGUI_DataModel.dict_object["Case"]:
                mess = cfdstudyMess.trMessage(
                    self.tr("REMOVE_ACTION_CONFIRM_MESS"), [itemPath])
            elif itemId == CFDSTUDYGUI_DataModel.dict_object["RESUSubFolder"]:
                mess = cfdstudyMess.trMessage(
                    self.tr("REMOVE_RESU_SUB_FOLDER_ACTION_CONFIRM_MESS"), [itemPath])
            elif itemId == CFDSTUDYGUI_DataModel.dict_object["RESUSubErrFolder"]:
                mess = cfdstudyMess.trMessage(
                    self.tr("REMOVE_RESU_SUB_FOLDER_ACTION_CONFIRM_MESS"), [itemPath])
            elif itemId == CFDSTUDYGUI_DataModel.dict_object["RESU_COUPLINGSubFolder"]:
                mess = cfdstudyMess.trMessage(
                    self.tr("REMOVE_RESU_SUB_FOLDER_ACTION_CONFIRM_MESS"), [itemPath])
            else:
                mess = cfdstudyMess.trMessage(
                    self.tr("REMOVE_FILE_ACTION_CONFIRM_MESS"), [itemPath])
            if cfdstudyMess.warningMessage(mess) == QMessageBox.No:
                return

            if itemId == CFDSTUDYGUI_DataModel.dict_object["Case"]:
                casePath = twItem.text(col.details)
                self.getSolverGUI().removeTab(casePath)

            watchCursor = QCursor(Qt.WaitCursor)
            QApplication.setOverrideCursor(watchCursor)
            # --- As we remove case directory which can be the current working directory,
            #     we need to change the current working directory otherwise there is a problem with os.getcwd() or equivalent
            fatherItem = twItem.parent()
            fatherpath = os.path.dirname(itemPath)
            os.chdir(fatherpath)
            if os.path.isdir(itemPath):
                shutil.rmtree(itemPath)
            elif os.path.isfile(itemPath):
                os.remove(itemPath)
            self.getClientGui().getCLSMainWindow().initialSelection(fatherItem)
            QApplication.restoreOverrideCursor()
            CFDSTUDYGUI_DataModel.getCFDTW().rebuildTWRecursively(fatherItem)

    # TODO verif utilisation, reecrire avec twi
    def slotCopyInDATA(self):
        """
        """
        logging.debug("slotCopyInDATA")
        sobj = self._singleSelectedObject()
        if sobj != None:
            path = CFDSTUDYGUI_DataModel._GetPath(sobj)
            study = CFDSTUDYGUI_DataModel._getStudy()
            builder = study.NewBuilder()

            attr = builder.FindOrCreateAttribute(sobj, "AttributeLocalID")
            parent = sobj.GetFather()
            if not parent == None:
                parent = parent.GetFather()

                if not parent == None and parent.GetName() == "DATA":
                    parentPath = CFDSTUDYGUI_DataModel._GetPath(parent)
                    newpath = os.path.join(parentPath, sobj.GetName())
                    if os.path.exists(newpath):
                        mess = cfdstudyMess.trMessage(
                            self.tr("OVERWRITE_CONFIRM_MESS"), [])
                        if cfdstudyMess.warningMessage(mess) == QMessageBox.No:
                            return

                    shutil.copy2(path, parentPath)
                    self.updateObjBrowser(parent)

    # TODO verif utilisation, reecrire avec twi

    def slotCopyInSRC(self):
        """
        """
        logging.debug("slotCopyInSRC")
        sobj = self._singleSelectedObject()
        if sobj != None:
            path = CFDSTUDYGUI_DataModel._GetPath(sobj)
            parent = sobj.GetFather()
            if not parent == None:
                if not parent == None and (parent.GetName() != "DRAFT" and parent.GetName() != "REFERENCE" and parent.GetName() != "EXAMPLES"):
                    parent = parent.GetFather()
                if not parent == None and (parent.GetName() == "REFERENCE" or parent.GetName() == "DRAFT" or parent.GetName() == "EXAMPLES"):
                    parentName = parent.GetName()
                    parent = parent.GetFather()
                    if not parent == None and parent.GetName() == "SRC":
                        parentPath = CFDSTUDYGUI_DataModel._GetPath(parent)
                        destPath = os.path.join(parentPath, sobj.GetName())
                        if parentName == "EXAMPLES" and '-' in sobj.GetName():
                            a, b = sobj.GetName().split('-')
                            c = b.split('.')[-1]
                            newName = '.'.join([a, c])
                            destPath = os.path.join(parentPath, newName)
                        if os.path.exists(destPath):
                            mess = cfdstudyMess.trMessage(
                                self.tr("OVERWRITE_CONFIRM_MESS"), [])
                            if cfdstudyMess.warningMessage(mess) == QMessageBox.No:
                                return
                        shutil.copy2(path, parentPath)
                        if parentName == "EXAMPLES" and '-' in sobj.GetName():
                            os.rename(os.path.join(parentPath, sobj.GetName()),
                                      os.path.join(parentPath, newName))
                        self.updateObjBrowser(parent)

    def slotMoveToDRAFT(self):
        """
        """
        logging.debug("slotMoveToDRAFT")
        if self.selectedItem:
            twItem = self.selectedItem
            path = twItem.text(col.details)
            parent = twItem.parent()
            if parent:
                parentPath = os.path.join(parent.text(col.details), 'DRAFT')
                destPath = os.path.join(parentPath, twItem.text(col.name))
                if os.path.exists(destPath):
                    mess = cfdstudyMess.trMessage(
                        self.tr("OVERWRITE_CONFIRM_MESS"), [])
                    if cfdstudyMess.warningMessage(mess) == QMessageBox.No:
                        return
                    else:
                        os.remove(destPath)

                if os.path.exists(parentPath) == False:
                    os.mkdir(parentPath)
                if CFDSTUDYGUI_DataModel.isLinkPathItem(twItem):
                    # --- symbolic link file
                    shutil.copy(path, parentPath)
                    import subprocess
                    ret = subprocess.call(['rm', '-f', path])
                else:
                    shutil.move(path, parentPath)
                getCFDTW().UpdateSubTree(parent)

    def _singleSelectedObject(self):
        """
        """
        study = CFDSTUDYGUI_DataModel._getStudy()
        if sg.SelectedCount() == 1:
            entry = sg.getSelected(0)
            if entry != '':
                return study.FindObjectID(entry)
        return None

    def _multipleSelectedObject(self):
        """
        """
        study = CFDSTUDYGUI_DataModel._getStudy()

        i = 0
        liste_SObj = []
        while i < sg.SelectedCount():
            entry = sg.getSelected(i)
            if entry != '':
                liste_SObj.append(study.FindObjectID(entry))
            i = i+1
        return liste_SObj

    def slotExportInParavis(self):
        """
        Not used now, but will be used when PARAVIS API will run correctly
        """
        logging.debug("slotExportInParavis")
        if self.selectedItem is not None:
            import pvsimple
            import salome
            path = self.selectedItem.text(col.details)
            name = self.selectedItem.text(col.name)

            pvsimple.ShowParaviewView()
            if re.match(".*\.med$", name) or re.match(".*\.case$", name):
                # export result file from CFDSTUDY into PARAVIS
                engine = salome.lcc.FindOrLoadComponent(
                    "FactoryServer", "PARAVIS")
                renderView1 = pvsimple.GetActiveViewOrCreate('RenderView')
                pvsimple.OpenDataFile(path)
                DataRepresentation = pvsimple.Show()
                renderView1.ResetCamera()

            if re.match(".*\.csv$", name):
                # export csv file from CFDSTUDY into PARAVIS
                engine = salome.lcc.FindOrLoadComponent(
                    "FactoryServer", "PARAVIS")
                coord_path = pvsimple.CSVReader(FileName=[path])
                renderView1 = pvsimple.GetActiveViewOrCreate('RenderView')
                viewLayout1 = pvsimple.GetLayout()
                pvsimple.OpenDataFile(path)
                # Create a new 'SpreadSheet View'
                spreadSheetView1 = pvsimple.CreateView('SpreadSheetView')
                # place view in the layout
                # viewLayout1.AssignView(2, spreadSheetView1)
                # show data in view
                coord_Display = pvsimple.Show(coord_path, spreadSheetView1)

            if sg.hasDesktop():
                sg.updateObjBrowser()
        QApplication.restoreOverrideCursor()

    def slotExportInSMESH(self):
        """
        Open the selected MED file in SMESH
        Fill the tree widget with all the mesh groups present in the MED file.
        """
        logging.debug("slotExportInSMESH")
        waitCursor = QCursor(Qt.WaitCursor)
        QApplication.setOverrideCursor(waitCursor)

        if self.selectedItem is not None:
            path = self.selectedItem.text(col.details)
            entry = self.getClientGui().importMedMesh(path)
            self.selectedItem.setText(col.entry, entry)

        QApplication.restoreOverrideCursor()

    def slotShow(self):
        """
        """
        item = self.selectedItem
        path = self.selectedItem.text(col.details)
        if path:
            # --- selection is the mesh itself
            self.slotExportInSMESH()
            entryMesh = item.text(col.entry)
            logging.debug("menu show mesh %s", entryMesh)
            sgPyQt.activateViewManagerAndView(self.getClientGui().getVTKViewer())
            salome.sg.Display(entryMesh)
            self.getClientGui().setColor(entryMesh)
        else:
            # --- selection is a group or a type of groups (nodes, faces, solids...)
            entry = item.text(col.entry)
            logging.debug("menu show group(s) %s", entry)
            sgPyQt.activateViewManagerAndView(self.getClientGui().getVTKViewer())
            nbChildren = item.childCount()
            if nbChildren:
                for i in range(nbChildren):
                    chitm = item.child(i)
                    entry = chitm.text(col.entry)
                    if entry:
                        salome.sg.Display(entry)
                        self.getClientGui().setColor(entry)
            else:
               if entry:
                   salome.sg.Display(entry)
                   self.getClientGui().setColor(entry)
        salome.sg.FitAll()

    def slotShowOnly(self):
        """
        """
        item = self.selectedItem
        entry = item.text(col.entry)
        logging.debug("menu show only%s", entry)
        sgPyQt.activateViewManagerAndView(self.getClientGui().getVTKViewer())
        path = self.selectedItem.text(col.details)
        if path:
            # --- selection is the mesh itself
            if entry:
                salome.sg.DisplayOnly(entry)
                self.getClientGui().setColor(entry)
        else:
            # --- selection is a group or a type of groups (nodes, faces, solids...)
            nbChildren = item.childCount()
            if nbChildren:
                for i in range(nbChildren):
                    chitm = item.child(i)
                    entry = chitm.text(col.entry)
                    if entry:
                        if i == 0:
                            salome.sg.DisplayOnly(entry)
                        else:
                            salome.sg.Display(entry)
                        self.getClientGui().setColor(entry)
            else:
                if entry:
                    salome.sg.DisplayOnly(entry)
                    self.getClientGui().setColor(entry)
        salome.sg.FitAll()

    def slotHide(self):
        """
        """
        item = self.selectedItem
        entry = item.text(col.entry)
        logging.debug("menu hide %s", entry)
        sgPyQt.activateViewManagerAndView(self.getClientGui().getVTKViewer())
        path = self.selectedItem.text(col.details)
        if path:
            # --- selection is the mesh itself
            if entry:
                isVisible = salome.sg.IsInCurrentView(entry)
                logging.debug("isInCurrentView %s, %s", entry, isVisible)
                logging.debug(" hide mesh %s", entry)
                salome.sg.Erase(entry)
        else:
            # --- selection is a group or a type of groups (nodes, faces, solids...)
            nbChildren = item.childCount()
            if nbChildren:
                for i in range(nbChildren):
                    chitm = item.child(i)
                    entry = chitm.text(col.entry)
                    if entry:
                        isVisible = salome.sg.IsInCurrentView(entry)
                        logging.debug("isInCurrentView %s, %s", entry, isVisible)
                        logging.debug(" hide mesh %s", entry)
                        salome.sg.Erase(entry)
            else:
                if entry:
                    isVisible = salome.sg.IsInCurrentView(entry)
                    logging.debug("isInCurrentView %s, %s", entry, isVisible)
                    logging.debug(" hide mesh %s", entry)
                    salome.sg.Erase(entry)

    def slotFitAll(self):
        item = self.selectedItem
        entry = item.text(col.entry)
        sgPyQt.activateViewManagerAndView(self.getClientGui().getVTKViewer())
        logging.debug("menu FitAll %s", entry)
        salome.sg.FitAll()

    def OpenCFD_GUI(self, item):
        """
        Open into Salome the CFD GUI from an XML file, given it's tree item
        """
        logging.debug("OpenCFD_GUI")
        import os
        id = item.text(col.id)
        if id != str(CFDSTUDYGUI_DataModel.dict_object["DATAfileXML"]):
            logging.debug("wrong type of file")
            return
        caseItem = CFDSTUDYGUI_DataModel.getCFDTW().findCaseItem(item)
        studyItem = CFDSTUDYGUI_DataModel.getCFDTW().findStudyItem(caseItem)
        aXmlFileName = item.text(col.name)
        aCaseName = caseItem.text(col.name)
        aStudyName = studyItem.text(col.name)
        aCase = CFDSTUDYGUI_DataModel.getCFDTW().getObjFromTwi(caseItem)

        if CFDSTUDYGUI_SolverGUI.findDockWindow(aXmlFileName, aCaseName, aStudyName):
            mess = cfdstudyMess.trMessage(self.tr("ALREADY_OPEN"), [
                                          aStudyName, aCaseName, aXmlFileName])
            cfdstudyMess.aboutMessage(mess)
            return

        # xml case file not already opened
        wm = self._SolverGUI.ExecGUI(self.solverParentWidget,
                                     aXmlFileName, caseItem)
        self.updateActions()

    def slotOpenCFD_GUI(self):
        """
        Open into Salome the CFD GUI from an XML file whose name is sobj.GetName()
        """
        logging.debug("slotOpenCFD_GUI")
        # TODO: rewrite
        item = self.selectedItem
        sobj = None
        if item:
            sobj = getCFDTW().getObjFromEntry(item.text(col.entry))
        if sobj != None:
            import os
            if not os.path.exists(CFDSTUDYGUI_DataModel._GetPath(sobj)):
                mess = cfdstudyMess.trMessage(self.tr("ENV_DLG_INVALID_FILE"), [CFD_Code(
                ), CFDSTUDYGUI_DataModel._GetPath(sobj)])+self.tr("STMSG_UPDATE_STUDY_INCOMING")
                cfdstudyMess.aboutMessage(mess)
                getCFDTW().UpdateSubTree(item)
                return
            self.OpenCFD_GUI(sobj)

    def slotOpenAnExistingCaseFileFromMenu(self):
        """
        Open into Salome the CFD GUI an existing XML file case from the Gui menu and not from Object browser
        """
        logging.debug("slotOpenAnExistingCaseFileFromMenu")
        boo = False
        StudyPath = ""
        CaseName = ""
        xmlfileName = ""
        title = cfdstudyMess.trMessage(
            self.tr("OPEN_EXISTING_CASE_GUI_TEXT"), [])
        xmlfileName, _ = QFileDialog.getOpenFileName(
            None, title, QDir.currentPath(), "*.xml")
        xmlfileName = str(xmlfileName)
        if xmlfileName == "":
            return
        boo, StudyPath, CasePath = self.checkCFDCaseDir(xmlfileName)
        if boo and StudyPath != "" and CasePath != "":
            CaseName = os.path.basename(CasePath)
            iok = getCFDTW()._SetCaseLocation(CasePath)
            studyObj = getCFDTW().FindStudyObjectByPath(StudyPath)
            logging.debug("studyObj %s CaseName %s",
                          studyObj.getEntry(), CaseName)
            caseObj = getCFDTW().getSObject(studyObj, CaseName)
            caseTwi = getCFDTW().entryToTwi[caseObj.GetID()]
            DATATwi = getCFDTW().getTwiChildWithName(caseTwi, "DATA")
            XMLTwi = getCFDTW().getTwiChildWithName(DATATwi, os.path.basename(xmlfileName))
            codeName = CFDSTUDYGUI_DataModel.getNameCodeFromXmlCasePath(
                xmlfileName)
            self.OpenCFD_GUI(XMLTwi)
            self.updateActionsXmlFileItem(XMLTwi)

    def reloadCases(self, casesToReload):
        getCFDTW().reloadCases(casesToReload)

    def checkCFDCaseDir(self, filepath):
        """
        Check if filepath is an XML file which belong to a CFD case directory
        The structure of the case directory must include DATA RESU SRC directory
        """
        logging.debug("checkCFDCaseDir")
        boo = True
        StudyPath = ""
        CasePath = ""
        if not os.path.exists(filepath):
            mess = cfdstudyMess.trMessage(
                self.tr("ENV_DLG_INVALID_FILE"), [CFD_Code(), filepath])
            cfdstudyMess.aboutMessage(mess)
            return False, StudyPath, CasePath

        # Test if filepath is a CFD xml file for Code_Saturne or NEPTUNE_CFD
        codeName = CFDSTUDYGUI_DataModel.getNameCodeFromXmlCasePath(filepath)
        if codeName == "":
            boo = False
            mess = cfdstudyMess.trMessage(
                self.tr("ENV_DLG_INVALID_FILE_XML"), [CFD_Code(), filepath])
            cfdstudyMess.aboutMessage(mess)
            return boo, StudyPath, CasePath
        else:
            _SetCFDCode(codeName)

        repDATA = os.path.dirname(filepath)
        if os.path.isdir(repDATA) and os.path.basename(repDATA) == "DATA":
            CasePath = os.path.dirname(repDATA)
            boo = CFDSTUDYGUI_Commons.isaCFDCase(CasePath)
            if not boo:
                mess = cfdstudyMess.trMessage(
                    self.tr("ENV_DLG_CASE_FILE"), [filepath, CasePath])
                cfdstudyMess.aboutMessage(mess)
                return boo, StudyPath, CasePath
            StudyPath = os.path.dirname(CasePath)
        else:
            boo = False
            mess = cfdstudyMess.trMessage(
                self.tr("ENV_INVALID_DATA_FILE_XML"), [CFD_Code(), filepath])
            cfdstudyMess.warningMessage(mess)
        return boo, StudyPath, CasePath

    def CloseCFD_GUI(self, twi):
        """
        Close into Salome the CFD GUI from an XML file whose name is sobj.GetName()
        """
        logging.debug("CloseCFD_GUI")
        id = twi.text(col.id)
        if id == str(CFDSTUDYGUI_DataModel.dict_object["Case"]):
            casePath = twi.text(col.details)
            self.getSolverGUI().removeTab(casePath)
        else:
            caseTwi = getCFDTW().findCaseItem(twi)
            if caseTwi:
                casePath = caseTwi.text(col.details)
                self.getSolverGUI().removeTab(casePath)

    def slotCloseCFD_GUI(self):
        """
        Close into Salome the CFD GUI from an XML file whose name is sobj.GetName()
        """
        logging.debug("slotCloseCFD_GUI")
        item = self.selectedItem
        self.CloseCFD_GUI(item)

    def slotUndo(self):
        self._SolverGUI.onUndo()

    def slotRedo(self):
        self._SolverGUI.onRedo()

    def slotLaunchGUI(self, study=None, case=None):
        """
        Build the command line for the GUI of Code_Saturne/NEPTUNE_CFD.
        Launch a new CFD GUI with popup menu on case object into SALOME Object browser
        the selected item should be a caseItem (popup menu item only available in this case)
        """
        caseItem = self.selectedItem
        itemName = caseItem.text(col.name)
        logging.debug("slotLaunchGUI %s", itemName)
        # get current selection
        idText = caseItem.text(col.id)
        id = 0
        if id is not None:
            id = int(idText)
        logging.debug("item id %s", id)
        if id == CFDSTUDYGUI_DataModel.dict_object["Case"]:
            wm = self._SolverGUI.ExecGUI(
                self.solverParentWidget, None, caseItem)
            self.updateActions()

    def slotUpdateCasePath(self):
        logging.debug("slotUpdateCasePath")
        caseItem = self.selectedItem
        if not caseItem:
            return
        casePath = caseItem.text(col.details)
        if not os.path.exists(casePath):
            mess = cfdstudyMess.trMessage(self.tr("ENV_DLG_INVALID_DIRECTORY"), [
                                          casePath]) + self.tr("STMSG_UPDATE_STUDY_INCOMING")
            cfdstudyMess.aboutMessage(mess)
            return
        CFDSTUDYGUI_DataModel.updateCasePath(casePath)

    def slotMeshConvertToMed(self):
        """
        """
        logging.debug("slotMeshConvertToMed")
        study = CFDSTUDYGUI_DataModel._getStudy()

        sg = CFDSTUDYGUI_DataModel.sg
        if sg.SelectedCount() != 1:
            # no selection
            return
        elif sg.SelectedCount() == 1:
            sobj = self._singleSelectedObject()
            medFile = str(QFileInfo(sobj.GetName()).baseName())
            self.DialogCollector.ECSConversionDialog.setResultFileName(medFile)

        self.DialogCollector.ECSConversionDialog.exec_()
        if not self.DialogCollector.ECSConversionDialog.result() == QDialog.Accepted:
            return

        aFirtsObj = None
        if sg.SelectedCount() == 1:
            aFirtsObj = self._singleSelectedObject()
        else:
            list_obj = self._multipleSelectedObject()
            if not list_obj == []:
                aFirtsObj = list_obj[0]
            else:
                return

        aStudyObj = CFDSTUDYGUI_DataModel.GetStudyByObj(aFirtsObj)

        aMeshFold = aFirtsObj.GetFather()
        thePath = CFDSTUDYGUI_DataModel._GetPath(aMeshFold)
        logging.debug("slotMeshConvertToMed -> thePath = %s" % thePath)
        args = ""

        b, c, mess = BinCode()
        if mess != "":
            cfdstudyMess.criticalMessage(mess)
        else:
            args = c

            outfile = self.DialogCollector.ECSConversionDialog.resultFileName()

            args += " --no-write "
            args += " --case "
            args += enquote_arg(os.path.join(thePath, outfile))
            args += " --post-volume "
            args += " med "
            args += CFDSTUDYGUI_DataModel._GetPath(sobj)

            logging.debug("slotMeshConvertToMed -> args = %s" % args)
            dlg = CFDSTUDYGUI_CommandMgr.CFDSTUDYGUI_QProcessDialog(sgPyQt.getDesktop(),
                                                                    self.tr(
                                                                        "STMSG_ECS_CONVERT"),
                                                                    [args],
                                                                    sobj.GetFather(),
                                                                    thePath)
            dlg.show()

    def slotRunScript(self):
        """
        """
        logging.debug("slotRunScript")
        sobj = self._singleSelectedObject()
        if sobj:
            curd = os.path.abspath('.')
            father = sobj.GetFather()
            fatherpath = CFDSTUDYGUI_DataModel._GetPath(father)
            path = CFDSTUDYGUI_DataModel._GetPath(sobj)

            # check exec rights
            if not os.access(path, os.F_OK or os.X_OK):
                mess = cfdstudyMess.trMessage(
                    self.tr("RUN_SCRIPT_ACTION_ACCESS_ERROR"), [])
                cfdstudyMess.criticalMessage(mess)
                return

            dlg = CFDSTUDYGUI_CommandMgr.CFDSTUDYGUI_QProcessDialog(sgPyQt.getDesktop(),
                                                                    self.tr(
                                                                        "STMSG_RUN_SCRIPT"),
                                                                    [path],
                                                                    father,
                                                                    fatherpath)
            dlg.show()

    def slotSaveDataFile(self):
        """
        Redirects B{Save} method to GUI of current solver
        """
        logging.debug("slotSaveDataFile")
        xmlDefaultName = "setup.xml"
        xmlFilePath = self._SolverGUI.SaveXmlFile()
        if xmlFilePath == None:
            return
        if os.path.basename(xmlFilePath) == xmlDefaultName:
            theCase = self._SolverGUI.getCase(self._SolverGUI._CurrentWindow)
            if theCase == None:
                return
            if xmlDefaultName not in CFDSTUDYGUI_DataModel.getXmlCaseNameList(theCase):
                oldXmlFilePath = None
                self.updateGui(oldXmlFilePath, xmlFilePath)

    def slotSaveAsDataFile(self):
        logging.debug("slotSaveAsDataFile")
        oldXmlFilePath, xmlFilePath = self._SolverGUI.SaveAsXmlFile()
        self.updateGui(oldXmlFilePath, xmlFilePath)

    def updateGui(self, oldXmlFilePath, xmlFilePath):
        logging.debug("updateGui")
        if oldXmlFilePath == xmlFilePath:
            return
        if xmlFilePath == None:
            return
        if oldXmlFilePath == None:
            oldCase = self._SolverGUI.getCase(self._SolverGUI._CurrentWindow)
            oldStudy = CFDSTUDYGUI_DataModel.GetStudyByObj(oldCase)
            self._SolverGUI.removeDockWindow(
                oldStudy.GetName(), oldCase.GetName(), "unnamed")
        else:
            # Close the old CFD xml from SALOME study
            boo, StudyPath, CasePath = self.checkCFDCaseDir(oldXmlFilePath)
            if boo and StudyPath != "" and CasePath != "":
                CaseName = os.path.basename(CasePath)
                studyObj = getCFDTW().getSObject.FindStudyObjectByPath(StudyPath)
                caseObj = getCFDTW().getSObject(studyObj, CaseName)
                DATAObj = getCFDTW().getSObject(caseObj, "DATA")
                XMLObj = getCFDTW().getSObject(DATAObj, os.path.basename(oldXmlFilePath))
                self.CloseCFD_GUI(XMLObj)
                self.updateActionsXmlFile(XMLObj)

       # Open the save as CFD xml GUI
        boo, StudyPath, CasePath = self.checkCFDCaseDir(xmlFilePath)
        if boo and StudyPath != "" and CasePath != "":
            iok = getCFDTW()._SetStudyLocation(theStudyPath=StudyPath,
                                               theCaseName=CasePath,
                                               theCreateOpt=False,
                                               theCopyOpt=False,
                                               theNameRef="",
                                               theSyrthesOpt=False,
                                               theSyrthesCase="",
                                               theNprocs="")
            CaseName = os.path.basename(CasePath)
            studyObj = getCFDTW().FindStudyObjectByPath(StudyPath)
            caseObj = getCFDTW().getSObject(studyObj, CaseName)
            DATAObj = getCFDTW().getSObject(caseObj, "DATA")
            XMLObj = getCFDTW().getSObject(DATAObj, os.path.basename(xmlFilePath))
            codeName = CFDSTUDYGUI_DataModel.getNameCodeFromXmlCasePath(
                xmlFilePath)
            self.OpenCFD_GUI(XMLObj)
            self.updateActionsXmlFile(XMLObj)

    def slotOpenShell(self):
        """
        Redirects B{OpenShell} method to GUI of current solver
        """
        logging.debug("slotOpenShell")
        self._SolverGUI.onOpenShell()

    def slotDisplayCurrentCase(self):
        """
        Redirects B{Display Current Case} method to GUI of current solver
        """
        logging.debug("slotDisplayCurrentCase")
        self._SolverGUI.onDisplayCase()

    def slotEditSRCFiles(self):
        """
        Manage and edit user SRC files of the currently open CASE.
        """
        logging.debug("slotDisplayCurrentCase")
        self._SolverGUI.onEditSRCFiles()

    def slotViewLogFiles(self):
        """
        View log files of the currently open CASE.
        """
        logging.debug("slotViewLogFiles")
        self._SolverGUI.onViewLogFiles()

    def slotCheckUsersCompilation(self):
        """
        Test compilation of user SRC files.
        """
        logging.debug("slotCheckUsersCompilation")
        self._SolverGUI.onCheckSRCFiles()

    def slotFileTransfer(self):
        """
        Open a File transfer widget to allow transfer between localhost and a
        distant host.
        Widget is in C++ and compiled with SALOME, hence the Popen call.
        """
        logging.debug("slotFileTransfer")
        popen = subprocess.Popen("remotefilebrowser", stdout=subprocess.PIPE)
        popen.wait()

    def slotLaunchSolver(self):
        """
        Manage and edit user SRC files of the currently open CASE.
        """
        logging.debug("slotLaunchSolver")
        self._SolverGUI.onLaunchSolver()

    def slotLaunchOT(self):
        """
        Transfer the CFD model to OpenTURNS
        """
        logging.debug("slotLaunchOT")
        self._SolverGUI.onLaunchOT()

    def slotHelpAbout(self):
        """
        Redirects B{About QDialog} display to GUI of current solver
        """
        logging.debug("slotHelpAbout")
        self._SolverGUI.onHelpAbout()

    def slotHelpLicense(self):
        logging.debug("slotHelpLicense")
        self._SolverGUI.onSaturneHelpLicense()

    def slotHelpUserGuide(self):
        logging.debug("slotHelpUserGuide")
        self._SolverGUI.onSaturneHelpManual()

    def slotHelpTutorial(self):
        logging.debug("slotHelpTutorial")
        self._SolverGUI.onSaturneHelpTutorial()

    def slotHelpTheory(self):
        logging.debug("slotHelpTheory")
        self._SolverGUI.onSaturneHelpKernel()

    def slotHelpRefcard(self):
        logging.debug("slotHelpRefcard")
        self._SolverGUI.onSaturneHelpRefcard()

    def slotHelpDoxygen(self):
        logging.debug("slotHelpDoxygen")
        self._SolverGUI.onSaturneHelpDoxygen()

    def slotHelpNCUserGuide(self):
        logging.debug("slotHelpNCUserGuide")
        self._SolverGUI.onNeptuneHelpManual()

    def slotHelpNCTutorial(self):
        logging.debug("slotHelpNCTutorial")
        self._SolverGUI.onNeptuneHelpTutorial()

    def slotHelpNCTheory(self):
        logging.debug("slotHelpNCTheory")
        self._SolverGUI.onNeptuneHelpKernel()

    def slotHelpNCDoxygen(self):
        logging.debug("slotHelpNCDoxygen")
        self._SolverGUI.onNeptuneHelpDoxygen()

    def slotOpenSyrthesCaseFile(self):
        """
        OpenSyrthesGui
        """
        logging.debug("slotOpenSyrthesCaseFile")
        sobj = self._singleSelectedObject()
        if not sobj == None:
            import salome
            import salome.syrthes
            from salome.syrthes.dictSyrthesDesc import SYR_DESC

            import SyrthesMain
            from SyrthesMain import MainView

            path = CFDSTUDYGUI_DataModel._GetPath(sobj)
            if re.match(".*\.syd$", sobj.GetName()):
                widget = MainView(sgPyQt.getDesktop(), False, True)
                widget.OpeningFile(path)
                widget.show()

            if sg.hasDesktop():
                sg.updateObjBrowser()
        QApplication.restoreOverrideCursor()

    def slotExportSyrInSmesh(self):
        """
        Export Syr syrthes file in SMESH
        """
        logging.debug("slotExportSyrInSmesh")
        waitCursor = QCursor(Qt.WaitCursor)
        QApplication.setOverrideCursor(waitCursor)

        sobj = self._singleSelectedObject()
        if sobj is None:
            return
        path = CFDSTUDYGUI_DataModel._GetPath(sobj)
        if smeshBuilder:
            smesh = smeshBuilder.New()
            study = CFDSTUDYGUI_DataModel._getStudy()
            builder = study.NewBuilder()
            meshcomponent = study.FindComponent("SMESH")
            if meshcomponent is None:
                meshcomponent = builder.NewComponent("SMESH")
                attr = builder.FindOrCreateAttribute(
                    meshcomponent, "AttributeName")
                attr.SetValue("SMESH")
            # --- loop on meshes to find if a mesh with the same path
            # and name is already loaded in SMESH
            MeshPath = ""
            iter = study.NewChildIterator(meshcomponent)
            while iter.More():  # --- loop on meshes
                studobj = iter.Value()
                iter.Next()
                object = studobj.GetObject()
                if object is None:
                    continue
                aMesh = object._narrow(SMESH.SMESH_Mesh)
                if aMesh is None:
                    continue
                medFileInfo = aMesh.GetMEDFileInfo()
                if medFileInfo == None:
                    continue
                aPath = medFileInfo.fileName
                # print "Mesh path:", aPath
                if path == aPath:
                    # print "same path"
                    MeshPath = aPath
                    break
                pass
            meshpathNewFile = ""
            # --- if the mesh is not already loaded in SMESH, load it
            if re.match(".*\.syr$", sobj.GetName()):
                meshpathNewFile = path.replace(".syr", ".med")
                comm = ['syrthes4med30', '-m', path, '-o', meshpathNewFile]
                import subprocess
                ret = subprocess.call(comm)
                path = meshpathNewFile
            if re.match(".*\.med$", sobj.GetName()) or meshpathNewFile != "":
                if MeshPath == "":
                    aMeshes, aStatus = smesh.CreateMeshesFromMED(path)
                    if not aStatus:
                        QApplication.restoreOverrideCursor()
                        mess = cfdstudyMess.trMessage(
                            self.tr("EXPORT_IN_SMESH_ACTION_WARNING"), [])
                        cfdstudyMess.warningMessage(mess)
                        return
                    for aMeshDC in aMeshes:
                        aMeshDC.SetAutoColor(1)
                        mesh = aMeshDC.GetMesh()
            sg.updateObjBrowser()

        QApplication.restoreOverrideCursor()

    def commonAction(self, theId):
        """
        Returns action by id from common action map of module
        """
        # logging.debug("commonAction id %s", theId)
        if not theId in self._CommonActionIdMap:
            raise ActionError("Invalid action id")

        action_id = self._CommonActionIdMap[theId]

        if action_id == None or not action_id in self._ActionMap:
            raise ActionError("Invalid action map content")
        return self._ActionMap[action_id]

    def solverAction(self, theId):
        """
        Returns action by id from solver action maps of module
        """
        # logging.debug("solverAction id %s", theId)
        action_id = None

        if theId in self._SolverActionIdMap:
            action_id = self._SolverActionIdMap[theId]
        elif theId in self._HelpActionIdMap:
            action_id = self._HelpActionIdMap[theId]

        if action_id == None:
            raise ActionError("Invalid action id")

        if not action_id in self._ActionMap:
            raise ActionError("Invalid action map content")

        return self._ActionMap[action_id]

    def connectSolverGUI(self):
        """
        Show all the dock windows of CFDSTUDY, when activating another Salome Component
        """
        logging.debug("connectSolverGUI")
        self._SolverGUI.connectDockWindows()

# -------------------------------------------------------------------------------
