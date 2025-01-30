# -*- coding: utf-8 -*-

import logging

import salome
salome.salome_init()
theStudy = salome.myStudy


def DumpMesh(aMeshName, fileMed):
    """
    Dump entries of a mesh

    The mesh is found in Salome study and its children are recursively explored
    to get the groupe type, entry and name.

    The result is a list of [type, entry, name, offset] where 
    type is the name given in Salome Study, for instance 'Groups of faces', 
    entry is the entry string from Salome Study,
    name is the group name in Salome Study,
    offset is the hierarchic level of child

    :param string aMeshName: the complete mesh path
    :return: list of [type, entry, name, offset]
    """
    logging.info("DumpMesh %s %s", aMeshName, fileMed)
    itcomp = salome.myStudy.NewComponentIterator()
    Builder = salome.myStudy.NewBuilder()
    liste = []
    candidats = []
    while itcomp.More():
        SO = itcomp.Value()
        name = SO.ComponentDataType()
        if name == "SMESH":
            it = salome.myStudy.NewChildIterator(SO)
            while it.More():
                CSO = it.Value()
                name = None
                found, AtName = Builder.FindAttribute(CSO, "AttributeName")
                if found:
                    name = AtName.Value()
                if name == aMeshName:
                    medFileInfo = CSO.GetObject().GetMesh().GetMEDFileInfo()
                    fileName = medFileInfo.fileName
                    logging.debug("medFileInfo.fileName %s", fileName)
                    if fileName == fileMed:
                        candidats.append(CSO)
                it.Next()
        itcomp.Next()
    if len(candidats) > 0:
        SO = candidats[-1]
        entryType = 'maillage'
        entry = SO.GetID()
        liste.append([entryType, entry, aMeshName, 0])
        liste = ExploreMesh(SO, Builder, liste, entryType, 0)
    return liste


def ExploreMesh(SO, Builder, liste, entryType, offset):
    """
    recursively iterates through children
    """
    logging.debug("ExploreMesh")
    it = salome.myStudy.NewChildIterator(SO)
    offset += 1
    while it.More():
        CSO = it.Value()
        entry = CSO.GetID()
        name = None
        found, AtName = Builder.FindAttribute(CSO, "AttributeName")
        if found:
            name = AtName.Value()
        liste.append([entryType, entry, name, offset])
        anEntryType = name
        liste = ExploreMesh(CSO, Builder, liste, anEntryType, offset)
        it.Next()
    return liste
