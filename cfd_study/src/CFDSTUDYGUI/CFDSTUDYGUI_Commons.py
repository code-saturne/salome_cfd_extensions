# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------

# This file is part of Code_Saturne, a general-purpose CFD tool.
#
# Copyright (C) 1998-2022 EDF S.A.
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
Common
======

"""
from code_saturne.gui.base.QtCore    import *

#-------------------------------------------------------------------------------
# Standard modules
#-------------------------------------------------------------------------------

import os, re, subprocess
import logging

#-------------------------------------------------------------------------------
# Salome modules
#-------------------------------------------------------------------------------
from CFDSTUDYGUI_Message import cfdstudyMess
# Get SALOME PyQt interface
import SalomePyQt
sgPyQt = SalomePyQt.SalomePyQt()

# Get SALOME Swig interface
import libSALOME_Swig
sg = libSALOME_Swig.SALOMEGUI_Swig()

#-------------------------------------------------------------------------------
# Application modules
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# Global variables
#-------------------------------------------------------------------------------

CFD_Saturne = "Code_Saturne"
CFD_Neptune = "NEPTUNE_CFD"

_CFD_solvers = {CFD_Saturne:'code_saturne',
                CFD_Neptune:'neptune_cfd'}

# ObjectTR is a convenient object for traduction purpose
ObjectTR = QObject()

# Main variable for solver
_CFD_Code = None #By default

# True or false for log tracing
_Trace = False  #

# If True all stdout redirected to MassageWindow
_LogModeOn = True

#---Enumerations---
#Event type for indicate of case in process
CaseInProcessStart  = -1000
CaseInProcessEnd    = -1001
UpdateScriptFolder  = -1002

#-------------------------------------------------------------------------------
# log config
#-------------------------------------------------------------------------------

logging.basicConfig()
log = logging.getLogger("CFDSTUDYGUI_Commons")
log.setLevel(logging.NOTSET)

#-------------------------------------------------------------------------------
# Functions definitions
#-------------------------------------------------------------------------------

def CFD_Code():
    global _CFD_Code
    return _CFD_Code

def getCFDSolverName(code_name=None):
    """
    Get cfd solver name.
    If 'code_name' is not provided, default value (CFD_Code()) is used.
    """
    solver_name = None

    if code_name == None:
        code_name = CFD_Code()

    if code_name in _CFD_solvers.keys():
        solver_name = _CFD_solvers[code_name]

    return solver_name

def _SetCFDCode(var):
    log.debug("_SetCFDCode : var = %s" % var)
    global _CFD_Code
    _CFD_Code = var


def Trace():
    global _Trace
    return _Trace


def LogModeOn():
    global _LogModeOn
    _LogModeOn = True


def LogModeOff():
    global _LogModeOn
    _LogModeOn = False


# check for available type of solver

def CheckCFD_CodeEnv(code):
    """
    This method try to found the config file of the CFD I{code}.

    @param code: name of the searching code (CFD_Saturne or CFD_Neptune).
    @type theType: C{String}
    @rtype: C{True} or C{False}
    @return: C{True} if the searching code is found.
    """
    mess = ""
    prefix = ""
    bindir = ""

    if code not in [CFD_Saturne, CFD_Neptune]:
        mess = cfdstudyMess.trMessage(ObjectTR.tr("CFDSTUDY_INVALID_SOLVER_NAME"),
                                      [code,CFD_Saturne,CFD_Neptune])
        iok= False
        return iok, mess

    else:
        iok = False
        _solver_name = getCFDSolverName(code);
        try:
            from code_saturne.base.cs_package import package
            pkg = package(name = _solver_name)
            b = os.path.join(pkg.get_dir('bindir'),
                             _solver_name+pkg.config.shext)
            if os.path.isfile(b):
                iok = True
            else:
                mess = cfdstudyMess.trMessage(ObjectTR.tr("INFO_DLG_INVALID_ENV"),
                                              [code]) + e.__str__()
                mess += cfdstudyMess.trMessage(ObjectTR.tr("CHECK_CODE_INSTALLATION"),
                                               [_solver_name,code])

        except:
            mess = cfdstudyMess.trMessage(ObjectTR.tr("INFO_DLG_INVALID_ENV"),
                                          [code]) + e.__str__()
            if "cs_package" in e.__str__():
                mess += cfdstudyMess.trMessage(ObjectTR.tr("CHECK_CODE_PACKAGE"),
                                               ["cs_package",code])
            elif _solver_name in e.__str__():
                mess += cfdstudyMess.trMessage(ObjectTR.tr("CHECK_CODE_PACKAGE"),
                                               [_solver_name,code])

    if iok:
        _solver_name = getCFDSolverName(code);
        pkg = package(name = _solver_name)
        prefix = pkg.get_dir('prefix')
        log.debug("CheckCFD_CodeEnv -> prefix = %s" % (prefix))

        bindir = pkg.get_dir('bindir')
        log.debug("CheckCFD_CodeEnv -> prefix = %s" % (bindir))

        if not os.path.exists(prefix):
            mess = cfdstudyMess.trMessage(ObjectTR.tr("ENV_DLG_INVALID_DIRECTORY"),
                                          [prefix])
            iok = False
        else:
            if not os.path.exists(bindir):
                mess = cfdstudyMess.trMessage(ObjectTR.tr("ENV_DLG_INVALID_DIRECTORY"),
                                              [bindir])
                iok = False

    log.debug("CheckCFD_CodeEnv -> %s = %s" % (code, iok))
    log.debug("CheckCFD_CodeEnv -> %s: %s" % (code, mess))
    return iok, mess


def BinCode():
    b = ""
    c = ""
    mess = ""
    # default package is code_saturne (for convert...)
    from code_saturne.base.cs_package import package

    try:
        _solver_name = getCFDSolverName()
    except:
        raise Exception("Uknown CFD solver: '%s'" % str(CFD_code()))

    pkg = package(name=_solver_name)

    b = os.path.join(pkg.get_dir('bindir'),
                     _solver_name+pkg.config.shext)
    c = pkg.get_preprocessor()
    log.debug("BinCode -> \n    %s\n    %s" % (b, c))
    return b, c, mess

def isaCFDCase(theCasePath):
    log.debug("isaCFDCase")
    dirList = []
    if os.path.isdir(theCasePath):
        dirList = os.walk(theCasePath).__next__()[1]
        if (dirList.count("DATA") or \
            dirList.count("SRC")):
            return True
    return False

def isaCFDStudy(theStudyPath):
    log.debug("isaCFDStudy")
    dirList = []
    if os.path.isdir(theStudyPath):
        dirList = os.walk(theStudyPath).__next__()[1]
        for i in dirList:
            if i not in ["MESH"] :
                if isaCFDCase(os.path.join(theStudyPath,i)) :
                    return True
    return False

def isSyrthesCase(theCasePath):
    log.debug("isSyrthesCase")
#a minima
    iok = True
    if os.path.isdir(theCasePath):
        dirList = os.listdir(theCasePath)
        if not dirList.count("Makefile") and not dirList.count("syrthes.py"):
            iok = False
    return iok

def isaSaturneSyrthesCouplingStudy(theStudyPath):
    log.debug("isaSaturneSyrthesCouplingStudy")
    iok = False
    hasCFDCase     = False
    hasSyrthesCase = False
    if not os.path.isdir(theStudyPath):
        mess = cfdstudyMess.trMessage(ObjectTR.tr("MUST_BE_A_DIRECTORY"),[theStudyPath])
        cfdstudyMess.criticalMessage(mess)
        return False
    # TODO replace by a more robust test, using a query function of the
    # main code_saturne command or subcommand (to be added)
    dirList = os.listdir(theStudyPath)
    if not (dirList.count("RESU_COUPLING") and dirList.count("run.cfg")):
        return False
    for i in dirList:
        ipath = os.path.join(theStudyPath,i)
        if os.path.isdir(ipath):
            if i not in ["MESH", "RESU_COUPLING"]:
                if isaCFDCase(ipath):
                    hasCFDCase = True
                if isSyrthesCase(ipath):
                    hasSyrthesCase = True
    if hasCFDCase and hasSyrthesCase:
        iok = True
    return iok

#-------------------------------------------------------------------------------
# Classes definitions
#-------------------------------------------------------------------------------

class LoggingAgent:
    def __init__(self, stream ):
        self.stream = stream


    def write( self, Text ):
        global _LogModeOn
        global sgPyQt

        #self.stream.write( Text )

        if len(Text) == 0:
            return

        lst = re.split( "\n", Text )
        for s in lst:
            if not len(s) == 0:
                sgPyQt.message( re.sub('<','&lt;',re.sub( '>', '&gt;', s)), False )


    def close(self):
        return self.stream


class LoggingMgr:
    def __init__(self ):
        pass


    def start( self, sys_obj):
        self.AgentOut = LoggingAgent( sys_obj.stdout )
        sys_obj.stdout = self.AgentOut

        self.AgentErr = LoggingAgent( sys_obj.stderr )
        sys_obj.stderr = self.AgentErr


    def finish( self, sys_obj):

        if self.AgentOut != None:
            sys_obj.stdout = self.AgentOut.close()

        if self.AgentErr != None:
            sys_obj.stderr = self.AgentErr.close()
