# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------

# This file is part of Code_Saturne, a general-purpose CFD tool.
#
# Copyright (C) 1998-2012 EDF S.A.
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
Solver GUI
==========

The two solvers I{Code_Saturne} and C{NEPTUNE_CFD} have their own GUI. The
purpose of the class C{CFDSTUDYGUI_SolverGUI} is to display the solver GUI of
the selected code in the SALOME workspace.
"""

#-------------------------------------------------------------------------------
# Standard modules
#-------------------------------------------------------------------------------

import os, sys, string, logging

#-------------------------------------------------------------------------------
# Third-party modules
#-------------------------------------------------------------------------------

from PyQt4.QtGui import QApplication, QMainWindow, QDockWidget, QTreeView, QMessageBox
from PyQt4.QtCore import Qt, QObject, QEvent, SIGNAL, SLOT

#-------------------------------------------------------------------------------
# Salome modules
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# Application modules
#-------------------------------------------------------------------------------

from CFDSTUDYGUI_Commons import CFD_Code, CFD_Saturne, CFD_Neptune, sgPyQt
from CFDSTUDYGUI_Commons import LogModeOn, LogModeOff, LoggingMgr, LoggingAgent
import CFDSTUDYGUI_DataModel
from CFDSTUDYGUI_Management import CFDGUI_Management, _d_DockWindowsRuncase

#-------------------------------------------------------------------------------
# log config
#-------------------------------------------------------------------------------

logging.basicConfig()
log = logging.getLogger("CFDSTUDYGUI_SolverGUI")
log.setLevel(logging.DEBUG)
#log.setLevel(logging.NOTSET)

#-------------------------------------------------------------------------------
# Global definitions
#-------------------------------------------------------------------------------

mw = None

def getObjectBrowserDock():
    dock = None
    dsk = sgPyQt.getDesktop()
    studyId = sgPyQt.getStudyId()
    for dock in dsk.findChildren(QDockWidget):
        dockTitle = str(dock.windowTitle())
        if (dockTitle == 'Object Browser'):
            return dock

#-------------------------------------------------------------------------------
# Function definitions
#-------------------------------------------------------------------------------

_c_CFDGUI = CFDGUI_Management()


def tabObjectBrowser():
    """
    tabify DockWidgets which contains QTreeView:
    Object Browser and CFDSTUDY tree
    """
    dsk = sgPyQt.getDesktop()
    ldock = dsk.findChildren(QDockWidget)
    ldocktree = []
    for i in ldock:
        lo = i.findChildren(QTreeView)
        if len(lo):
            ldocktree.append(i)
    for i in range(1, len(ldocktree)):
        dsk.tabifyDockWidget(ldocktree[0], ldocktree[i])


def updateObjectBrowser():
    """
    force le regroupement en onglets des QTreeView apres updateObjBrowser
    """
    studyId = sgPyQt.getStudyId()
    sgPyQt.updateObjBrowser(studyId, 1)
    tabObjectBrowser()


def findDockWindow( xmlName, caseName, studyCFDName):
    """
    Find if the dockwindow corresponding to this xmlcase is already opened
    """
    bool_findDockWindow = False

    if _c_CFDGUI != None:
        bool_findDockWindow = _c_CFDGUI.findElem(xmlName, caseName, studyCFDName)

    return bool_findDockWindow


#-------------------------------------------------------------------------------
# Classes definition
#-------------------------------------------------------------------------------

class CFDSTUDYGUI_SolverGUI(QObject):
    """
    Auxilliary class for interaction with solvers GUI
    """
    def __init__(self):
        log.debug("CFDSTUDY_SolverGUI.__init__: ")
        QObject.__init__(self, None)
        self._CurrentWindow = None


    def ExecGUI(self, WorkSpace, sobjXML, aCase, Args=''):
        """
        Executes GUI for solver relatively CFDCode
        """
        log.debug("CFDSTUDY_SolverGUI.ExecGUI: ")
        mw = None
        if sobjXML != None:
            #searching
            aTitle = sobjXML.GetName()
            if aCase != None:
                if findDockWindow(aTitle,aCase.GetName(),aCase.GetFather().GetName()):
                    fileN = str(aCase.GetFather().GetName() + "." + aCase.GetName()) + '.' + str(aTitle)
                    mess = "Case file " + fileN + " is already opened"
                    QMessageBox.warning(None, "Warning: ",mess)
                    return
        else:
            aTitle = "unnamed"
            if aCase != None:
                if findDockWindow(aTitle,aCase.GetName(),aCase.GetFather().GetName()):
                    mess = "A case not finished to be set is already opened"
                    QMessageBox.warning(None, "Warning: ",mess)
                    return

        if aCase != None:
            # object of DATA folder
            aChildList = CFDSTUDYGUI_DataModel.ScanChildren(aCase, "^DATA$")
            if not len(aChildList)== 1:
                # no DATA folder
                log.debug("CFDSTUDYGUI_SolverGUI.ExecGUI:There are not data folder in selected by user case")
                return None
            aStartPath = CFDSTUDYGUI_DataModel._GetPath(aChildList[0])
            if aStartPath != None and aStartPath != '':
                os.chdir(aStartPath)

        mw = self.lauchGUI(WorkSpace, aCase, sobjXML, Args)
        if mw != None:
            self._CurrentWindow = mw

        return mw


    def isActive(self):
        return self._CurrentWindow != None


    def onSaveXmlFile(self):
        log.debug("onSaveXmlFile")
        if self._CurrentWindow != None:
            if self._CurrentWindow.case['xmlfile'] != "":
                self._CurrentWindow.fileSave()
            else:
                self.SaveAsXmlFile()


    def SaveAsXmlFile(self):
        """
        First: get the xmlfile name with the case (whose path is stored into the MainView Object)
        then save as into tne new xml file (the new name is stored into the case of the MainView Object instead of the old one)
        return old_xml_file,new_xml_file
        """
        old_xml_file = None
        xml_file = None

        if self._CurrentWindow != None:
            _sMainViewCase = self._CurrentWindow
            old_xml_file = _sMainViewCase.case['xmlfile']
            _sMainViewCase.fileSaveAs()
            xml_file = _sMainViewCase.case['xmlfile']

            if old_xml_file == "":
                old_xml_file = None

        return old_xml_file, xml_file


    def getDockTitleName(self,xml_file):
        """
        Build the Dock Title Name STUDY.CASE.file.xml with the entire file Name path
        """
        lnames = string.split(xml_file,"/")
        if len(lnames) < 4:
            return None
        xmlname   = lnames[-1]
        casename  = lnames[-3]
        studyname = lnames[-4]
        return string.join([studyname, casename, xmlname], ".")


    def getDockTitleNameFromOB(self, studyname, casename, xmlname):
        return string.join([studyname, casename, xmlname], ".")


    def onOpenShell(self):
        """
        """
        log.debug("onOpenShell")
        if self._CurrentWindow != None:
            self._CurrentWindow.openXterm()


    def onDisplayCase(self):
        log.debug("onDisplayCase")
        _LoggingMgr.start(sys)
        if self._CurrentWindow != None:

            self._CurrentWindow.displayCase()
        _LoggingMgr.finish(sys)


    def onHelpAbout(self):
        log.debug("onHelpAbout")
        if self._CurrentWindow != None:
            self._CurrentWindow.displayAbout()


    def onSaturneHelpLicense(self):
        """
        """
        log.debug("onSaturneHelpLicense")
        if self._CurrentWindow != None:
            self._CurrentWindow.displayLicence()
        return


    def onSaturneHelpCS(self):
        """
        """
        log.debug("onSaturneHelpcs")
        if self._CurrentWindow != None:
            if CFD_Code() == CFD_Saturne:
                self._CurrentWindow.displayCSManual()
        return


    def onSaturneHelpSD(self):
        """
        """
        log.debug("onSaturneHelpSD")
        if self._CurrentWindow != None:
            if CFD_Code() == CFD_Saturne:
                self._CurrentWindow.displayECSManual()
        return


    def onSaturneHelpCS_Kernel(self):
        """
        """
        log.debug("onSaturneHelpCS_Kernel")
        if self._CurrentWindow != None:
            if CFD_Code() == CFD_Saturne:
                self._CurrentWindow.displayCSKernel()

        return


    def onSaturneHelpCS_Infos(self):
        """
        """
        log.debug("onSaturneHelpCS_INFOS")
        if self._CurrentWindow != None:
            if CFD_Code() == CFD_Saturne:
                self._CurrentWindow.displayECSInfos()

        return


    def setWindowTitle_CFD(self,mw,aCase,baseTitleName):
        """
        """
        if aCase != None:
            fatherName = aCase.GetFather().GetName()
            aTitle = str(fatherName + "." + aCase.GetName()) + '.' + str(baseTitleName)
            if mw != None:
                mw.setWindowTitle(aTitle)
        return aTitle


    def lauchGUI(self, WorkSpace, aCase, sobjXML, Args):
        """
        mw.dockWidgetBrowser is the Browser of the CFD MainView
        """
        log.debug("lauchGUI")
        from cs_gui import process_cmd_line
        from cs_package import package
        from Base.MainView import MainView

        if CFD_Code() == CFD_Saturne:
            from cs_package import package
            from Base.MainView import MainView
        elif CFD_Code() == CFD_Neptune:
            from nc_package import package
            from core.MainView import MainView

        if sobjXML == None:
            Title = "unnamed"
        else:
            Title = sobjXML.GetName()

        self.Workspace = WorkSpace
        pkg = package()
        case, splash = process_cmd_line(Args)
        mw = MainView(pkg, case, aCase)

        aTitle = self.setWindowTitle_CFD(mw, aCase, Title)
        dsk = sgPyQt.getDesktop()
        dock = QDockWidget(aTitle)

        dock.setWidget(mw.frame)
        dock.setMinimumWidth(520)
        dsk.addDockWidget(Qt.RightDockWidgetArea, dock)

        studyId = sgPyQt.getStudyId()

        dock.setVisible(True)
        dock.show()

        BrowserTitle = aTitle  + " Browser"
        mw.dockWidgetBrowser.setWindowTitle(BrowserTitle)
        dsk.addDockWidget(Qt.LeftDockWidgetArea,mw.dockWidgetBrowser)

        mw.dockWidgetBrowser.setVisible(True)
        mw.dockWidgetBrowser.show()
        mw.dockWidgetBrowser.raise_()
        dock.raise_()

#MP Dock windows are managed by CFDGUI_Management class defined into CFDSTUDYGUI_Management.py

        aStudyCFD = aCase.GetFather()
        aCaseCFD  = aCase
        xmlFileName = str(Title)
        _c_CFDGUI.set_d_CfdCases(studyId, dock, mw.dockWidgetBrowser, mw, aStudyCFD, aCaseCFD, xmlFileName, sobjXML, None)

        self.connect(dock, SIGNAL("visibilityChanged(bool)"), self.setdockWindowBrowserActivated)
        self.connect(mw.dockWidgetBrowser, SIGNAL("visibilityChanged(bool)"),self.setdockWindowActivated)

        self.connect(dock.toggleViewAction(), SIGNAL("toggled(bool)"), self.setdockWB)
        self.connect(mw.dockWidgetBrowser.toggleViewAction(), SIGNAL("toggled(bool)"), self.setdock)

        _c_CFDGUI.tabifyDockWindows(dsk, studyId)
        self.showDockWindows(studyId, xmlFileName, aCaseCFD.GetName(), aStudyCFD.GetName())
        updateObjectBrowser()

        return mw


    def setdockWB(self, istoggled):
        studyId = sgPyQt.getStudyId()
        dock = self.sender().parent()
        if _c_CFDGUI != None:
          dockWB = _c_CFDGUI.getdockWB(studyId,dock)
          if dockWB != None:
            dockWB.setVisible(dock.isVisible())
            if istoggled: dockWB.setVisible(True)
            #
            if istoggled:
              dock.show()
              dock.raise_()
              dockWB.show()
              dockWB.raise_()
            mw = _c_CFDGUI.getMW(studyId,dock)
            self._CurrentWindow = mw
            mw.activateWindow()


    def setdock(self, istoggled):
        studyId = sgPyQt.getStudyId()
        dockWB = self.sender().parent()
        if _c_CFDGUI != None:
          dock = _c_CFDGUI.getdock(studyId,dockWB)
          if dock != None:
            dock.setVisible(dockWB.isVisible())
            if istoggled: dock.setVisible(True)
            if istoggled:
              dock.show()
              dock.raise_()
              dockWB.show()
              dockWB.raise_()
            mw = _c_CFDGUI.getMW(studyId,dock)
            self._CurrentWindow = mw
            mw.activateWindow()


    def setdockWindowBrowserActivated(self,visible):
        """
        mv is the Main CFD window allocated by MainView code
        When we click on a cfd study window tab, the cfd study window appears and the associated CFD window browser raises too
        """
        studyId = sgPyQt.getStudyId()
        dock = self.sender()
        if not visible:
            return
        if dock.isActiveWindow() == False:
            return
        if _c_CFDGUI != None:
          dockWB = _c_CFDGUI.getdockWB(studyId,dock)
          if dockWB != None:
            dockWB.activateWindow()
            dockWB.setVisible(True)
            dockWB.show()
            dockWB.raise_()
            mw = _c_CFDGUI.getMW(studyId,dock)
            self._CurrentWindow = mw
            mw.activateWindow()
            ob = sgPyQt.getObjectBrowser()
            # Clear the current selection in the SALOME object browser, which does not match with the shown dock window
            ob.clearSelection()


    def setdockWindowActivated(self,visible):
        """
        mv is the Main CFD window allocated by MainView code
        When we click on a  CFD window browser tab, the CFD window browser appears and the associated cfd study window raises too
        """
        dsk = sgPyQt.getDesktop()
        studyId = sgPyQt.getStudyId()
        dockWB = self.sender()

        if not visible:
            return
        if dockWB.isActiveWindow() == False:
            return
        if _c_CFDGUI != None:
          dock = _c_CFDGUI.getdock(studyId,dockWB)
          if dock != None:
            dock.activateWindow()
            dock.setVisible(True)
            dock.show()
            dock.raise_()
            mw = _c_CFDGUI.getMW(studyId,dock)
            self._CurrentWindow = mw
            mw.activateWindow()
            ob = sgPyQt.getObjectBrowser()
            # effacer la selection en cours
            ob.clearSelection()


    def disconnectDockWindows(self):
        """
        Hide the dock windows of CFDSTUDY GUI, when activating another Salome module
        We can have one or several of them with the right click on the main menu bar of
        Salome
        """
        studyId = sgPyQt.getStudyId()
        if _c_CFDGUI != None:
          _c_CFDGUI.hideDocks(studyId)

#MP runcase dock window is managed independently of the Management class CFDGUI_Management because it is not attached to an xml case in the CFD GUI
#MP to analyze: impact: CFDSTUDYGUI_CommandMgr.py (runTextEdit) and CFDSTUDYGUI_Management.py
        if studyId not in _d_DockWindowsRuncase.keys():
          return

        if len(_d_DockWindowsRuncase[studyId]) != 0:
            dock.hide()
            dock.toggleViewAction().setVisible(False)


    def connectDockWindows(self):
        """
        Show all the dock windows of CFDSTUDY GUI, when activating Salome CFDSTUDY module
        """
        studyId = sgPyQt.getStudyId()
        if _c_CFDGUI != None:
          _c_CFDGUI.showDocks(studyId)

        updateObjectBrowser()

#MP runcase dock window is managed independently of the Management class CFDGUI_Management because it is not attached to an xml case in the CFD GUI
#MP to analyze: impact: CFDSTUDYGUI_CommandMgr.py (runTextEdit) and CFDSTUDYGUI_Management.py
        if studyId not in _d_DockWindowsRuncase.keys():
          return

        if len(_d_DockWindowsRuncase[studyId]) != 0:
          for dock in _d_DockWindowsRuncase[studyId]:
            dock.show()
            dock.setVisible(True)
            dock.toggleViewAction().setVisible(True)


    def showDockWindows(self, studyId,xmlName, caseName, studyCFDName):
        """
        Find if the dockwindow corresponding to this xmlcase is already opened
        """
        if _c_CFDGUI != None:
            _c_CFDGUI.showDockWindows(studyId,xmlName, caseName, studyCFDName)


    def getStudyCaseXmlNames(self,mw):

        dsk = sgPyQt.getDesktop()
        studyId = sgPyQt.getStudyId()
        if _c_CFDGUI != None:
            studyCFDName,caseName,xmlName  = _c_CFDGUI.getStudyCaseXmlNames(studyId,mw)
        return studyCFDName,caseName,xmlName


    def getCase(self,mw):

        dsk = sgPyQt.getDesktop()
        studyId = sgPyQt.getStudyId()
        if _c_CFDGUI != None:
            case  = _c_CFDGUI.getCase(studyId,mw)
        return case


    def removeDockWindow(self,studyCFDName, caseName, xmlName=""):
        """
        Close the CFD_study_dock_windows from remove  popup menu in object browser
        """
        log.debug("removeDockWindow -> caseName = %s" % caseName)
        dsk = sgPyQt.getDesktop()
        studyId = sgPyQt.getStudyId()
        if _c_CFDGUI != None:
            _c_CFDGUI.delDock(dsk,studyId,studyCFDName, caseName, xmlName)
            updateObjectBrowser()
