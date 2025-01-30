# -*- coding: utf-8 -*-

import os
import logging
import colorsys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMenu, QMessageBox, QDockWidget
from PyQt5.QtCore import Qt, QObject

import salome
import SalomePyQt
from salome.smesh import smeshBuilder
# from qtsalome import QMenu

from code_saturne.base import cs_package


from .CLSMainWindow import CLSMainWindow
from .CLSMainWindow import getSalomePyQt
from .CLSMainWindow import col
from .utilstudy import DumpMesh
from .CFDSTUDYGUI_Commons import CheckCFD_CodeEnv, CFD_Saturne
from .CFDSTUDYGUI_Message import cfdstudyMess
from .CFDSTUDYGUI_ActionsHandler import CFDSTUDYGUI_ActionsHandler

salome.salome_init()

# ObjectTR is a convenient object for traduction purpose

ObjectTR = QObject()

_clientGui = None


def getClientGui():
    """
    access to the singleton instance of gui, created at first call
    """
    global _clientGui
    if _clientGui is None:
        logging.info("begin clientGui instanciate")
        _clientGui = ClientGui()
        logging.info("clientGui instanciated!")
    return _clientGui


def getCfdStudyViewType():
    return "CfdStudyWorkspace"


def BoundaryGroup():
    """
    Get a group name, its reference and type ("VOLUME", "FACE", "EDGE")
    """
    logging.debug("BoundaryGroup")
    # entry = getClientGui().getCurrentEntry()
    clsmainw = getClientGui().getCLSMainWindow()
    return clsmainw.getNameAndRef()


class ClientGui():
    """
    CFDSTUDY GUI SALOME Module
    """

    def __init__(self):
        """
        """
        logging.debug("__init__")
        self.smesh = None
        self.widget = None
        self.aboutToClose = False
        self._OCCViewer = 0
        self._VTKViewer = 0
        self._PVViewer = 0
        self.ah = None

        self.mainWindow = None
        self.clsmainw = None
        self.view = None

        self.currentEntry = ""
        self.currentFile = ""
        self.selectedItem = None

        self.meshNames = {}    # mesh name from entry (without path and ext)
        self.meshPaths = {}    # entry from mesh path
        self.meshColor = 0.25  # for HSV color
        self.actors = {}       # one color actor by entry

        self.casesToReload = []

    def getVTKViewer(self):
        return self._VTKViewer

    def getActionsHandler(self):
        return self.ah

    def initialize(self):
        """
        """
        logging.debug("initialize")

        # ObjectTR is a convenient object for traduction purpose

        self.ObjectTR = QObject()
        DEFAULT_EDITOR_NAME = self.ObjectTR.tr("CFDSTUDY_PREF_EDITOR")
        DEFAULT_READER_NAME = self.ObjectTR.tr("CFDSTUDY_PREF_READER")
        DEFAULT_DISPLAY_VIEWER_NAME = self.ObjectTR.tr(
            "CFDSTUDY_PREF_DISPLAY_VIEWER")
        if not getSalomePyQt().hasSetting("CFDSTUDY", "ExternalEditor"):
            getSalomePyQt().addSetting("CFDSTUDY", "ExternalEditor", DEFAULT_EDITOR_NAME)
        if not getSalomePyQt().hasSetting("CFDSTUDY", "ExternalReader"):
            getSalomePyQt().addSetting("CFDSTUDY", "ExternalReader", DEFAULT_READER_NAME)
        if not getSalomePyQt().hasSetting("CFDSTUDY", "ExternalDisplay"):
            getSalomePyQt().addSetting("CFDSTUDY", "ExternalDisplay", DEFAULT_DISPLAY_VIEWER_NAME)

        # preload code_saturne package to handle configuration file

        cs_root_dir = os.getenv('CS_ROOT_DIR')
        if cs_root_dir == None:
            try:
                import inspect
                p = inspect.getfile(cs_package)
                d = os.path.split(p)
                while d[1] != 'lib':
                    d = os.path.split(d[0])
                    cs_root_dir = d[0]
            except Exception:
                pass

        if cs_root_dir != None:
            config_file = (os.path.join(cs_root_dir,
                                        'lib',
                                        'code_saturne_build.cfg'))
            try:
                pkg = cs_package.package(config_file=config_file)
            except Exception:   # for compatibility with older versions
                pass

        pass

    def initSmesh(self):
        logging.debug("initSmesh")
        if self.smesh is None:
            logging.debug("init smesh: get a smeshBuilder instance")
            self.smesh = smeshBuilder.New()
        if not self._VTKViewer:
            logging.debug("init VTK Viewer %s", self._VTKViewer)
            self.clsmainw.ui.tw_central.setCurrentIndex(2)
            self._VTKViewer = getSalomePyQt().createView("VTKViewer", True, 0, 0, True)
            logging.debug("VTK Viewer: %s", self._VTKViewer)
            vtkwidget = getSalomePyQt().getViewWidget(self._VTKViewer)
            self.clsmainw.ui.gl_mesh.removeWidget(
                self.clsmainw.ui.wd_viewSmesh)
            self.clsmainw.ui.gl_mesh.addWidget(vtkwidget, 0, 0, 1, 1)
            self.clsmainw.ui.tw_central.setCurrentIndex(1)
            # --- Paraview Viewer and Geom Viewer are not used now: removed
            self.clsmainw.ui.tw_central.removeTab(2)
            self.clsmainw.ui.tw_central.removeTab(0)

    def activate(self):
        """
        """
        logging.debug("activate")
        views = getSalomePyQt().findViews(getCfdStudyViewType())
        if views:
            logging.debug("views found %s", views)
            getSalomePyQt().setViewVisible(views[0], True)
            view = views[0]
        else:
            self.mainWindow = getSalomePyQt().getDesktop()
            self.clsmainw = CLSMainWindow(self.mainWindow)
            view = getSalomePyQt().createView(getCfdStudyViewType(),
                                              self.clsmainw)
            logging.debug("create view %s", view)
            getSalomePyQt().setViewClosable(view, False)
            getSalomePyQt().setViewTitle(view, "Saturne workspace")
            self.clsmainw.initContextMenus(self.treeItemMenuMgr)
        logging.debug("activate view: %s", view)
        getSalomePyQt().activateView(view)
        self.clsmainw.setVisible(True)
        self.view = view
        self.clsmainw.ui.tw_central.setCurrentIndex(1)
        if self._VTKViewer:
            logging.debug(
                "activateViewManagerAndView VTK Viewer: %s", self._VTKViewer)
            getSalomePyQt().activateViewManagerAndView(self._VTKViewer)
        getSalomePyQt().enableSelector()
        self.initSmesh()
        if self.ah is None:
            self.ah = CFDSTUDYGUI_ActionsHandler()
            self.ah.createActions()

        env_saturne, msg = CheckCFD_CodeEnv(CFD_Saturne)
        logging.debug("activate -> env_saturne = %s" % env_saturne)
        if not env_saturne:
            QMessageBox.critical(getSalomePyQt().getDesktop(),
                                 "Error", msg, QMessageBox.Ok, 0)
            return False

        if msg != "":
            mess = cfdstudyMess.trMessage(self.ObjectTR.tr(
                "CFDSTUDY_INVALID_ENV"), []) + " ; " + msg
            cfdstudyMess.aboutMessage(msg)
            return False
        else:
            self.ah.DialogCollector.InfoDialog.setCode(env_saturne)
        self.ah.setSolverParentWidget(self.clsmainw.ui.tw_case)
        self.ah._SalomeSelection.currentSelectionChanged.connect(
            self.ah.updateActions)
        self.ah.connectSolverGUI()
        if len(self.casesToReload):
            self.ah.reloadCases(self.casesToReload)

        return True

    def closeStudy(self):
        self.aboutToClose = True

    def isAboutToClose(self):
        return self.aboutToClose

    def deactivate(self):
        """
        """
        global _clientGui
        logging.debug("deactivate")
        view = getSalomePyQt().findViews(getCfdStudyViewType())
        if view:
            getSalomePyQt().setViewVisible(view[0], False)
        getSalomePyQt().disableSelector()
        if self.isAboutToClose():
            _clientGui = None

    def save(self):
        """
        """
        logging.debug("save")

    def load(self):
        """
        """
        logging.debug("load")

    def close(self):
        """
        """
        logging.debug("close")

    def OnGUIEvent(self, commandID):
        """
        """
        logging.debug("OnGUIEvent: %s", commandID)

    def onSelectionUpdated(self, entryList):
        """
        """
        logging.debug("onSelectionUpdated %s", entryList)
        self.clsmainw.externSelectionChanged(entryList)

    def saveFiles(self, directory, url):
        """
        Called by SALOME when saving module's data in a SALOME study,
        The data to save will be written in a given temporary directory, 
        with a filename built with the SALOME study hdf filename and the module name
        """
        logging.debug("saveFiles %s %s", directory, url)
        from .CFDSTUDYGUI_DataModel import getCFDTW
        filename = os.path.join(directory, os.path.splitext(
            os.path.basename(url))[0]) + "_CFDSTUDY.txt"
        getCFDTW().saveFile(filename)
        return os.path.basename(filename)

    def openFiles(self, files, url):
        """
        Called by SALOME when opening a saved study, provides the filename to open, to reload items saved.
        files contains a temporary path and filename to be read, url is the study hdf file.
        """
        logging.debug("openFiles %s --- %s", files, url)
        from .CFDSTUDYGUI_DataModel import getCFDTW
        filename = os.path.join(*files)
        logging.debug("filename %s", filename)
        self.loadFile(filename)
        return True

    def loadFile(self, filename):
        '''
        Read text file and publish it.
        '''
        logging.debug("loadFile %s", filename)
        with open(filename,  mode='r', encoding='utf-8') as f:
            for line in f:
                casePath = line.split()[0]
                logging.debug("case: %s", casePath)
                if os.path.basename(casePath) != "MESH":
                    self.casesToReload.append(casePath)
        return True

    def setColor(self, entry):
        if entry in self.actors:
            return
        smg = salome.ImportComponentGUI('SMESH')
        actorPres = smg.properties(entry, self._VTKViewer)
        actorPres.opacity = 1.
        h = self.meshColor
        r, g, b = colorsys.hsv_to_rgb(h, 1., 1.)
        actorPres.nodeColor.r = r
        actorPres.nodeColor.g = g
        actorPres.nodeColor.b = b
        actorPres.surfaceColor.r = r
        actorPres.surfaceColor.g = g
        actorPres.surfaceColor.b = b
        actorPres.volumeColor.r = r
        actorPres.volumeColor.g = g
        actorPres.volumeColor.b = b
        logging.debug("parametres presentation acteur %s %s %s %s %s",
                      entry, actorPres.opacity,
                      actorPres.surfaceColor.r, actorPres.surfaceColor.g, actorPres.surfaceColor.b)
        smg.setProperties(entry, actorPres, self._VTKViewer)
        self.meshColor += 0.18
        self.actors[entry] = actorPres

    def importMedMesh(self, fileMed):
        """
        Import a mesh from a med file into SMESH and display the mesh,
        or just display the mesh if the med file is already loaded

        :param path fileMed: med file path

        :return: mesh entry in study
        :rtype: string
        """
        logging.debug("importMedMesh %s", fileMed)
        if not fileMed:
            return ""
        entryMesh = ""
        # --- if the mesh entry is already known, do nothing
        if fileMed in self.meshPaths.keys():
            entryMesh = self.meshPaths[fileMed]
        else:
            name = os.path.splitext(os.path.basename(fileMed))[0]
            # --- when reopening a study, the mesh is maybe already loaded
            found = False
            lso = salome.myStudy.FindObjectByName(name, "MESH")
            for sobject in lso:
                medFileInfo = sobject.GetObject().GetMesh().GetMEDFileInfo()
                existingFileMed = medFileInfo.fileName
                logging.debug("Med file already in study %s", existingFileMed)
                if existingFileMed == fileMed:
                    found = True
            if found:
                logging.debug("mesh already in study: %s", name)
                entryMesh = sobject.GetID()
            else:
                self.initSmesh()
                ([aMesh], status) = self.smesh.CreateMeshesFromMED(fileMed)
                medFileInfo = aMesh.GetMesh().GetMEDFileInfo()
                logging.debug("medFileInfo %s", medFileInfo)
                self.smesh.SetName(aMesh.GetMesh(), name)
            self.clsmainw.ui.tw_central.setCurrentIndex(1)
            liste = DumpMesh(name, fileMed)
            logging.debug("mesh published %s", liste)
            entryMesh = liste[0][1]
            logging.debug("entryMesh %s", entryMesh)
            self.meshPaths[fileMed] = entryMesh
            self.meshNames[entryMesh] = name
            self.clsmainw.detailsMeshGroups(fileMed, self.selectedItem, liste)
        logging.debug("entryMesh %s", entryMesh)
        return entryMesh

    def getTWSelectedItems(self):
        return self.clsmainw.ui.tw_gauche.selectedItems()

    def treeItemMenuMgr(self, position):
        """
        Defines all the specific actions related to each item of the tree
        """
        logging.debug("treeItemMenuMgr")
        menu = QMenu()
        self.currentEntry = ""
        self.currentFile = ""
        self.selectedItem = None
        items = self.clsmainw.ui.tw_gauche.selectedItems()
        if len(items) > 0:
            item = items[0]
            self.selectedItem = item
            self.ah.customPopup(item, menu)
        menu.exec_(self.clsmainw.ui.tw_gauche.viewport().mapToGlobal(position))

    def getCLSMainWindow(self):
        return self.clsmainw

    def createPreferences(self):
        logging.debug("createPreferences")
        genTab = getSalomePyQt().addPreference(ObjectTR.tr("CFDSTUDY_PREF_GEN_GROUP"))
        EditorField = str(ObjectTR.tr("EDITOR"))
        editorGroup = getSalomePyQt().addPreference(EditorField, genTab)
        externalEditorField = str(ObjectTR.tr("EXTERNAL_EDITOR"))
        externalReaderField = str(ObjectTR.tr("EXTERNAL_READER"))
        editor = getSalomePyQt().addPreference(externalEditorField, editorGroup,
                                               SalomePyQt.PT_String, "CFDSTUDY", "ExternalEditor")
        Reader = getSalomePyQt().addPreference(externalReaderField, editorGroup,
                                               SalomePyQt.PT_String, "CFDSTUDY", "ExternalReader")
        externalDisplayField = str(ObjectTR.tr("EXTERNAL_DISPLAY"))
        displayViewer = getSalomePyQt().addPreference(externalDisplayField, editorGroup,
                                                      SalomePyQt.PT_String, "CFDSTUDY", "ExternalDisplay")
