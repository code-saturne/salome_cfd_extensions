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

# -------------------------------------------------------------------------------

"""
Solver GUI
==========

The two solvers I{Code_Saturne} and C{NEPTUNE_CFD} have their own GUI. The
purpose of the class C{CFDSTUDYGUI_SolverGUI} is to display the solver GUI of
the selected code in the SALOME workspace.
"""

# -------------------------------------------------------------------------------
# Standard modules
# -------------------------------------------------------------------------------

import os
import sys
import logging

# -------------------------------------------------------------------------------
# Third-party modules
# -------------------------------------------------------------------------------

from code_saturne.gui.base.QtCore import *
from code_saturne.gui.base.QtGui import *
from code_saturne.gui.base.QtWidgets import *

# -------------------------------------------------------------------------------
# Salome modules
# -------------------------------------------------------------------------------

# -------------------------------------------------------------------------------
# Application modules
# -------------------------------------------------------------------------------

from .CFDSTUDYGUI_Commons import CFD_Code, CFD_Saturne, CFD_Neptune, getCFDSolverName, sgPyQt, sg
from .CFDSTUDYGUI_Commons import LoggingMgr
from . import CFDSTUDYGUI_DataModel
from .CFDSTUDYGUI_Management import CFDGUI_Management
from .constants import col
from code_saturne.base import cs_info
from code_saturne.base import cs_run_conf

# -------------------------------------------------------------------------------
# Global definitions
# -------------------------------------------------------------------------------

mw = None

_c_CFDGUI = CFDGUI_Management()

# -------------------------------------------------------------------------------
# Function definitions
# -------------------------------------------------------------------------------


def findObjectBrowserDockWindow():
    dsk = sgPyQt.getDesktop()
    ldock = []
    if dsk != None:
        ldock = dsk.findChildren(QDockWidget)
    objectBrowserDockWindow = None
    if ldock != []:
        for i in ldock:
            if 'Object Browser' in str(i.windowTitle()):
                objectBrowserDockWindow = i
    return objectBrowserDockWindow


def tabifyCfdGui():
    """
    tabify DockWidgets which contains CFD study CASE QMainview :
    CFDSTUDY Main Window
    """
    logging.debug("tabifyCfdGui")
    dsk = sgPyQt.getDesktop()
    ldockMainWin = []

    ldockMainWin = _c_CFDGUI.getDockListe()

    objectBrowserDockWindow = findObjectBrowserDockWindow()
    if len(ldockMainWin) >= 1:
        dsk.splitDockWidget(objectBrowserDockWindow,
                            ldockMainWin[0], Qt.Horizontal)
        dsk.tabifyDockWidget(objectBrowserDockWindow, ldockMainWin[0])
    for i in range(1, len(ldockMainWin)):
        dsk.tabifyDockWidget(ldockMainWin[0], ldockMainWin[i])
        dsk.tabifyDockWidget(objectBrowserDockWindow, ldockMainWin[i])


def updateObjectBrowser():
    """
    force le regroupement en onglets des QTreeView apres updateObjBrowser
    """
    sg.updateObjBrowser()
    tabifyCfdGui()


def findDockWindow(xmlName, caseName, studyCFDName):
    """-
    Find if the dockwindow corresponding to this xmlcase is already opened
    """
    logging.debug("findDockWindow")
    bool_findDockWindow = False

    if _c_CFDGUI != None:
        bool_findDockWindow = _c_CFDGUI.findElem(
            xmlName, caseName, studyCFDName)

    return bool_findDockWindow


# -------------------------------------------------------------------------------
# Classes definition
# -------------------------------------------------------------------------------

class CFDSTUDYGUI_SolverGUI(QObject):
    """
    Auxilliary class for interaction with solvers GUI
    """

    def __init__(self):
        logging.debug("CFDSTUDY_SolverGUI.__init__: ")
        QObject.__init__(self, None)
        self._CurrentWindow = None
        self.dockMainWin = None
        self._isActive = False
        self.tabWidget = None
        self.casePathToMainWin = {}
        self.casePathToMw = {}
        from .clientgui import getClientGui
        self.getClientGui = getClientGui
        from .CFDSTUDYGUI_DataModel import getCFDTW
        self.getCFDTW = getCFDTW

    def ExecGUI(self, parentWidget, xmlFileName, caseTwi):
        """
        Executes GUI for solver relatively CFDCode
        """
        logging.debug("CFDSTUDY_SolverGUI.ExecGUI: %s", xmlFileName)
        mw = None
        aTitle = xmlFileName
        aStartPath = None
        caseName = None
        studyName = None

        if caseTwi:
            caseName = caseTwi.text(col.name)
            studyTwi = caseTwi.parent()
            studyName = studyTwi.text(col.name)
            dataTwi = CFDSTUDYGUI_DataModel.getCFDTW().getTwiChildWithName(caseTwi, "DATA")
            if dataTwi is None:
                # --- no DATA folder
                mess = "DATA directory is not present in the case"
                QMessageBox.warning(None, "Warning: ", mess)
                return None
            aStartPath = dataTwi.text(col.details)
            if aStartPath == '':
                aStartPath = None  # To simplify further tests

        if xmlFileName:
            # --- check for already opened case
            if caseTwi:
                if findDockWindow(aTitle, caseName, studyName):
                    fileN = str(studyName + "." + caseName()) + \
                        '.' + str(aTitle)
                    mess = "Case file " + fileN + " is already opened"
                    QMessageBox.warning(None, "Warning: ", mess)
                    return
        else:
            if aStartPath:
                run_conf_path = os.path.join(aStartPath, 'run.cfg')
                if os.path.isfile(run_conf_path):
                    run_conf = cs_run_conf.run_conf(run_conf_path)
                    xmlFileName = run_conf.get('setup', 'param')
            if xmlFileName == None:
                aTitle = 'setup.xml'

        if caseTwi:
            if aStartPath:
                os.chdir(aStartPath)
        logging.debug("aStartPath: %s", aStartPath)
        mw = self.launchGUI(parentWidget, caseTwi, xmlFileName)
        if mw != None:
            self._CurrentWindow = mw
        self._isActive = True

        return mw

    def setCurrentWindow(self, newMW):
        logging.debug("setCurrentWindow %s", newMW)
        for casePath, mw in self.casePathToMainWin.items():
            # logging.debug("casePath %s mw %s", casePath, mw)
            if mw == newMW:
                logging.debug("casePath %s", casePath)
                self._CurrentWindow = self.casePathToMw[casePath]
                twi = self.getCFDTW().getTwiFromPath(casePath)
                logging.debug("twi %s", twi.text(col.name))
                self.getClientGui().getCLSMainWindow().caseSelectionChanged(twi)
                break

    def isActive(self):
        return self._isActive

    def okToContinue(self):
        logging.debug("okToContinue")
        if self._CurrentWindow != None and self._CurrentWindow.okToContinue():
            if self._CurrentWindow.case['probes']:
                self._CurrentWindow.case['probes'].removeActors()
            return True
        else:
            return False

    def SaveXmlFile(self):
        logging.debug("SaveXmlFile")
        xml_file = None
        if self._CurrentWindow != None:
            self._CurrentWindow.fileSave()
            xml_file = self._CurrentWindow.case['xmlfile']
        return xml_file

    def SaveAsXmlFile(self):
        """
        First: get the xmlfile name with the case (whose path is stored into the MainView Object)
        then save as into tne new xml file (the new name is stored into the case of the MainView Object instead of the old one)
        return old_xml_file,new_xml_file
        """
        old_xml_file = None
        xml_file = None
        if self._CurrentWindow != None:
            old_xml_file = self._CurrentWindow.case['xmlfile']
            self._CurrentWindow.fileSaveAs()
            xml_file = self._CurrentWindow.case['xmlfile']
            if old_xml_file == "":
                old_xml_file = None
            if xml_file == "":
                xml_file = None

        return old_xml_file, xml_file

    def getDockTitleName(self, xml_file):
        """
        Build the Dock Title Name STUDY.CASE.file.xml with the entire file Name path
        """
        lnames = xml_file.split("/")
        if len(lnames) < 4:
            return None
        xmlname = lnames[-1]
        casename = lnames[-3]
        studyname = lnames[-4]
        return '.'.join([studyname, casename, xmlname])

    def getDockTitleNameFromOB(self, studyname, casename, xmlname):
        return '.'.join([studyname, casename, xmlname])

    def onUndo(self):
        if self._CurrentWindow != None:
            self._CurrentWindow.slotUndo()

    def onRedo(self):
        if self._CurrentWindow != None:
            self._CurrentWindow.slotRedo()

    def onOTStudyMode(self):
        if self._CurrentWindow != None:
            self._CurrentWindow.slotOpenTurnsMode()

    def onOpenShell(self):
        if self._CurrentWindow != None:
            self._CurrentWindow.openXterm()

    def onDisplayCase(self):
        if self._CurrentWindow != None:
            self._CurrentWindow.displayCase()

    def onEditSRCFiles(self):
        if self._CurrentWindow != None:
            self._CurrentWindow.fileEditorOpen()

    def onCheckSRCFiles(self):
        if self._CurrentWindow != None:
            self._CurrentWindow.testUserFilesCompilation()

    def onViewLogFiles(self):
        if self._CurrentWindow != None:
            self._CurrentWindow.fileViewerOpen()

    def onLaunchSolver(self):
        if self._CurrentWindow != None:
            self._CurrentWindow.runOrSubmit()

    def onLaunchOT(self):
        if self._CurrentWindow != None:
            self._CurrentWindow.runOTMode()

    def onHelpAbout(self):
        if self._CurrentWindow != None:
            self._CurrentWindow.displayAbout()

    def onSaturneHelpLicense(self):
        if self._CurrentWindow != None:
            self._CurrentWindow.displayLicence()

    def onSaturneHelpManual(self):
        from code_saturne.base.cs_package import package
        argv_info = ['--guide', 'user']
        cs_info.main(argv_info, package())

    def onSaturneHelpTutorial(self):
        from code_saturne.base.cs_package import package
        msg = "See http://code-saturne.org web site for tutorials."
        QMessageBox.about(self._CurrentWindow, 'code_saturne Interface', msg)

    def onSaturneHelpKernel(self):
        from code_saturne.base.cs_package import package
        argv_info = ['--guide', 'theory']
        cs_info.main(argv_info, package())

    def onSaturneHelpRefcard(self):
        from code_saturne.base.cs_package import package
        argv_info = ['--guide', 'refcard']
        cs_info.main(argv_info, package())

    def onSaturneHelpDoxygen(self):
        from code_saturne.base.cs_package import package
        argv_info = ['--guide', 'Doxygen']
        cs_info.main(argv_info, package())

    def onNeptuneHelpManual(self):
        from code_saturne.base.cs_package import package
        argv_info = ['--guide', 'user']
        cs_info.main(argv_info, package(name='neptune_cfd'))

    def onNeptuneHelpTutorial(self):
        from code_saturne.base.cs_package import package
        argv_info = ['--guide', 'tutorial']
        cs_info.main(argv_info, package(name='neptune_cfd'))

    def onNeptuneHelpKernel(self):
        from code_saturne.base.cs_package import package
        argv_info = ['--guide', 'theory']
        cs_info.main(argv_info, package(name='neptune_cfd'))

    def onNeptuneHelpDoxygen(self):
        from code_saturne.base.cs_package import package
        argv_info = ['--guide', 'Doxygen']
        cs_info.main(argv_info, package(name='neptune_cfd'))

    def setWindowTitle_CFD(self, mw, caseTwi, baseTitleName):
        caseName = caseTwi.text(col.name)
        studyName = caseTwi.parent().text(col.name)
        aTitle = studyName + '.' + caseName + '.' + baseTitleName
        if mw != None:
            mw.setWindowTitle(aTitle)
        return aTitle

    def launchGUI(self, tabWidget, caseTwi, xmlFileName):
        """
        mw.dockWidgetBrowser is the Browser of the CFD MainView
        """
        casePath = caseTwi.text(col.details)
        logging.debug("launchGUI %s", casePath)
        self.tabWidget = tabWidget
        # --- if there is already a solver GUI for this case path, return it
        if casePath in self.casePathToMw:
            mw = self.casePathToMw[casePath]
            # retreive the tab index to select it
            tabIndex = -1
            self.mainWin = self.casePathToMainWin[casePath]
            nbTabs = tabWidget.count()
            for i in range(nbTabs):
                wd = tabWidget.widget(i)
                for c in wd.children():
                    if "QMainWindow" in str(c.__class__):
                        if c == self.mainWin:
                            tabIndex = i
                            break
            tabWidget.setCurrentIndex(tabIndex)
            return mw
        # --- otherwise, create it
        from code_saturne.gui.cs_gui import process_cmd_line
        from code_saturne.gui.base.MainView import MainView
        from code_saturne.base.cs_package import package
        from .clientgui import getClientGui

        self.Workspace = tabWidget

        if tabWidget.tabText(0) == "CFD case not defined":
            tabWidget.removeTab(0)

        # Get current solver name
        _solver_name = getCFDSolverName()
        pkg = package(name=_solver_name)

        args = []
        if xmlFileName != None:
            args = ['-p', xmlFileName]
            Title = xmlFileName
        else:
            Title = 'setup.xml'

        case, splash = process_cmd_line(args)
        try:
            mw = MainView(pkg, case, caseTwi)
        except:
            mess = "Error in Opening CFD GUI"
            QMessageBox.warning(None, "Warning", mess, QMessageBox.Ok,
                                QMessageBox.NoButton)
            return None

        # Put the standard panel of the MainView inside a QDockWidget
        # in the SALOME Desktop
        aTitle = self.setWindowTitle_CFD(mw, caseTwi, Title)
        # dsk = sgPyQt.getDesktop()

        # objectBrowserDockWindow = findObjectBrowserDockWindow()

        self.mainWin = QMainWindow()
        self.mainWin.setWindowTitle(aTitle)
        self.mainWin.setCentralWidget(mw.centralwidget)
        self.mainWin.addDockWidget(Qt.LeftDockWidgetArea, mw.dockWidgetBrowser)

        wd_case = QWidget()
        gl_case = QGridLayout(wd_case)
        self.mainWin.setParent(wd_case)
        gl_case.addWidget(self.mainWin, 0, 0, 1, 1)
        indexTab = tabWidget.addTab(wd_case, aTitle)
        tabWidget.setCurrentIndex(indexTab)
        self.casePathToMainWin[casePath] = self.mainWin
        self.casePathToMw[casePath] = mw

        getClientGui().getCLSMainWindow().setHSplitterSizes(300, 600, 750)
        updateObjectBrowser()
        return mw

    def removeTab(self, casePath):
        logging.debug("removeTab %s", casePath)
        if self.tabWidget and casePath in self.casePathToMainWin:
            mainWin = self.casePathToMainWin[casePath]
            tabIndex = -1
            nbTabs = self.tabWidget.count()
            for i in range(nbTabs):
                wd = self.tabWidget.widget(i)
                for c in wd.children():
                    if "QMainWindow" in str(c.__class__):
                        if c == mainWin:
                            tabIndex = i
                            break
            logging.debug("tabIndex %s", tabIndex)
            self.tabWidget.removeTab(tabIndex)
            self.casePathToMainWin.pop(casePath)
            self.casePathToMw.pop(casePath)

    def resizeObjBrowserDock(self):
        """
        called by closeStudy in CFDSTUDYGUI.py because the Object Browser size is stored into ~/.config/salome/SalomeApprc.xxx file xxx is the salome version
        """
        logging.debug(
            "resizeObjectBrowserDock ***************************************************************************************")

    def resizeMainWindowDock(self, visible):
        """
        visible referred to Object Browser dock widget
        """
        logging.debug(
            "resizeMainWindowDock ********************************************************************************************")

    def resizeObjectBrowserDock(self, visible):
        """
        visible referred to Object Browser dock widget
        """
        logging.debug(
            "resizeObjectBrowserDock ******************************************************************************************")

    def hideDocks(self):
        _c_CFDGUI.hideDocks()
        ob = sgPyQt.getObjectBrowser()
        # Clear the current selection in the SALOME object browser, which does not match with the shown dock window
        if ob != None:
            ob.clearSelection()

    def showDocks(self):
        _c_CFDGUI.showDocks()
        ob = sgPyQt.getObjectBrowser()
        # Clear the current selection in the SALOME object browser, which does not match with the shown dock window
        if ob != None:
            ob.clearSelection()

    def disconnectDockWindows(self):
        """
        Hide the dock windows of CFDSTUDY GUI, when activating another Salome module
        We can have one or several of them with the right click on the main menu bar of
        Salome
        """
        if _c_CFDGUI != None:
            if _c_CFDGUI.d_CfdCases != []:
                self.hideDocks()

    def connectDockWindows(self):
        """
        Show all the dock windows of CFDSTUDY GUI, when activating Salome CFDSTUDY module
        """
        logging.debug("connectDockWindows")
        if _c_CFDGUI != None:
            if _c_CFDGUI.d_CfdCases != []:
                self.showDocks()
                tabifyCfdGui()

    def getStudyCaseXmlNames(self, mw):
        if _c_CFDGUI != None:
            studyCFDName, caseName, xmlName = _c_CFDGUI.getStudyCaseXmlNames(
                mw)
        return studyCFDName, caseName, xmlName

    def getCase(self, mw):
        if _c_CFDGUI != None:
            case = _c_CFDGUI.getCase(mw)
        return case

    def removeDockWindowfromStudyAndCaseNames(self, studyCFDName, caseName):
        """
        Close the CFD_study_dock_windows if opened from close Study popup menu
        into the object browser
        """
        logging.debug("removeDockWindowfromStudyAndCaseNames -> %s %s" %
                      (studyCFDName, caseName))
        dsk = sgPyQt.getDesktop()
        if _c_CFDGUI != None:
            _c_CFDGUI.delDockfromStudyAndCaseNames(dsk, studyCFDName, caseName)

    def removeDockWindow(self, studyCFDName, caseName, xmlName):
        """
        Close the CFD_study_dock_windows from remove  popup menu in object browser
        """
        logging.debug("removeDockWindow -> %s %s %s" %
                      (studyCFDName, caseName, xmlName))
        dsk = sgPyQt.getDesktop()
        if _c_CFDGUI != None:
            _c_CFDGUI.delDock(dsk, studyCFDName, caseName, xmlName)

# -------------------------------------------------------------------------------
