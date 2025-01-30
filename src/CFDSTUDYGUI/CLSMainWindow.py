# -*- coding: utf-8 -*-

import os
import logging

import SalomePyQt
from qtsalome import QMainWindow, QTreeWidgetItem, QAbstractItemView, QSize, Qt

from .mw_cfdstudy_ui import Ui_mw_Saturne

from .constants import col

_sgPyQt = None


def getSalomePyQt():
    global _sgPyQt
    if _sgPyQt is None:
        _sgPyQt = SalomePyQt.SalomePyQt()
    return _sgPyQt


class CLSMainWindow(QMainWindow):

    def __init__(self, parent):
        """
        Initialize the treeWidget for Saturne cases
        """
        QMainWindow.__init__(self, parent)
        logging.debug("__init__")
        self.ui = Ui_mw_Saturne()
        self.ui.setupUi(self)
        self.ui.tw_gauche.setColumnCount(5)
        self.ui.tw_gauche.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.saturneFolder = QTreeWidgetItem()
        self.saturneFolder.setText(col.name, "CFD Studies")
        self.saturneFolder.setText(col.ref, "REF")
        self.saturneFolder.setText(col.details, "details")
        self.saturneFolder.setText(col.entry, "entry")
        self.saturneFolder.setText(col.id, "id")
        self.ui.tw_gauche.hideColumn(col.ref)
        self.ui.tw_gauche.hideColumn(col.entry)
        self.ui.tw_gauche.hideColumn(col.id)
        self.ui.tw_gauche.addTopLevelItem(self.saturneFolder)
        self.ui.tw_gauche.itemSelectionChanged.connect(
            self.treeSelectionChanged)
        self.ui.tw_case.removeTab(1)
        self.ui.tw_case.currentChanged.connect(self.slotSelectTabCase)
        self.saturneItems = {}       # Tree item from case path
        self.saturneCondMeshes = {}  # Tree item from conduction mesh file path
        self.saturneRayMeshes = {}   # Tree item from radiation mesh file path
        self.entryItems = {}         # Entry from tree item
        self.treeItemMenuMgr = None
        self.selectedEntry = None
        self.selectedItem = None
        self.selectedParent = None
        from .clientgui import getClientGui
        self.getClientGui = getClientGui

    def setHSplitterSizes(self, l1, l2, l3):
        self.ui.splitter.setSizes([l1, l2, l3])

    def getSaturneFolder(self):
        return self.saturneFolder

    def getCurrentSelectedItem(self):
        return self.selectedItem

    def expandTree(self):
        self.ui.tw_gauche.expandToDepth(3)
        self.ui.tw_gauche.resizeColumnToContents(0)

    def removeItem(self, item):
        logging.debug("removeItem %s", item.text(col.name))
        parent = item.parent()
        self.selectedParent = parent
        parent.removeChild(item)

    def initialSelection(self, item):
        """
        Useful when tree widget is first filled with a study and nothing was selected,
        to detect the current study from menu/toolbar
        """
        twiSelected = self.ui.tw_gauche.selectedItems()
        if self.ui.tw_gauche.selectedItems():
            logging.debug("initialSelection %s",
                          twiSelected[0].text(col.details))
        logging.debug("set an initial selection on tree widget")
        self.ui.tw_gauche.setCurrentItem(item)
        self.treeSelectionChanged()

    def initContextMenus(self, treeItemMenuMgr):
        """
        The specific actions menus for each tree item are defined in clientgui.treeItemMenuMgr
        @see clientgui.activate
        """
        logging.debug("initContextMenus")
        self.treeItemMenuMgr = treeItemMenuMgr
        self.ui.tw_gauche.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.tw_gauche.customContextMenuRequested.connect(
            self.treeItemMenuMgr)

    def slotSelectTabCase(self):
        indexTab = self.ui.tw_case.currentIndex()
        logging.debug("slotSelectTabCase %s", indexTab)
        if indexTab<0:
            return
        currentWd = self.ui.tw_case.currentWidget()
        mw_case = None
        for c in currentWd.children():
            logging.debug("child %s", c.__class__)
            if "QMainWindow" in str(c.__class__):
                mw_case = c
                break
        ah = self.getClientGui().getActionsHandler()
        ah.getSolverGUI().setCurrentWindow(mw_case)
        # logging.debug("index: %s", self.ui.tw_case.indexOf(currentWd))

    def detailsMeshGroups(self, medFile, meshItem, liste):
        """
        Generate tree items for each group in a mesh

        :param string medFile: path of the med file.
        :param QTreeWidgetItem meshItem: QTreeWidgetItem associated to the meshFile
        :param list liste: a list of (parent, entry, name, offset) for each child
                           of the mesh in SALOME study (@see utilsstudy.DumpMesh)
        """
        from .CFDSTUDYGUI_DataModel import dict_object
        logging.debug("detailsMeshGroups %s %s", medFile, liste)
        if meshItem is None:
            logging.debug("meshItem is None")
            return
        groupTypes = ("faces", "nodes", "edges", "volumes")
        parentItem = meshItem
        for (parent, entry, name, offset) in liste:
            # --- offset 0 gives the entry and name of the mesh in Salome Study
            if offset == 0:
                meshItem.setText(col.entry, entry)
                self.entryItems[entry] = meshItem
            # --- offset 1 gives the groupType entry and name in Salome Study
            elif offset == 1:
                groupTypeItem = QTreeWidgetItem()
                groupTypeItem.setText(col.name, name)
                groupTypeItem.setText(col.entry, entry)
                groupTypeItem.setText(col.id, str(dict_object["Display"]))
                self.entryItems[entry] = groupTypeItem
                meshItem.addChild(groupTypeItem)
                parentItem = groupTypeItem
            # --- offset 2 gives groupType(parent), group entry and name in Salome Study.
            else:
                groupItem = QTreeWidgetItem()
                groupItem.setText(col.name, name)
                # groupItem.setText(col.ref, ref)
                groupItem.setText(col.entry, entry)
                groupItem.setText(col.id, str(dict_object["Display"]))
                self.entryItems[entry] = groupItem
                parentItem.addChild(groupItem)
        self.ui.tw_gauche.expandItem(meshItem)
        self.ui.tw_gauche.resizeColumnToContents(0)

    def treeSelectionChanged(self):
        """
        Called when one or more items are selected in the tree
        """
        logging.debug("new tree selection")
        selectedItems = self.ui.tw_gauche.selectedItems()
        if selectedItems:
            self.selectedItem = selectedItems[0]
            self.selectedParent = self.selectedItem.parent()
        else:
            self.selectedItem = self.selectedParent
        listEntries = []
        for item in selectedItems:
            logging.debug("selection: %s %s", item.text(
                col.name), item.text(col.entry))
            self.selectedEntry = item.text(col.entry)
            listEntries.append(item.text(col.entry))
        getSalomePyQt().setSelection(listEntries)

    def externSelectionChanged(self, entryList):
        """
        Called when one or more items are selected outside the tree (in the view, for instance)
        """
        logging.debug("new extern selection: %s", entryList)
        for entry in entryList:
            self.selectedEntry = entry
            if entry in self.entryItems.keys():
                item = self.entryItems[entry]
                self.ui.tw_gauche.setCurrentItem(item)

    def caseSelectionChanged(self, twi):
        logging.debug("caseSelectionChanged %s", twi)
        if twi:
            self.ui.tw_gauche.setCurrentItem(twi)

    def getNameAndRef(self):
        """
        From selected item,
        return the group name, its reference and type ("VOLUME", "FACE", "EDGE")
        """
        entry = self.selectedEntry
        logging.debug("getNameAndRef %s", entry)
        name = ""
        ref = ""
        typeGroup = ""
        if entry in self.entryItems.keys():
            item = self.entryItems[entry]
            name = item.text(col.name)
            ref = item.text(col.ref)
            parent = item.parent()
            if "face" in parent.text(col.name):
                typeGroup = "FACE"
            elif "edge" in parent.text(col.name):
                typeGroup = "EDGE"
            elif "volume" in parent.text(col.name):
                typeGroup = "VOLUME"
        return (name, ref, typeGroup)
