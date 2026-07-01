# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------------

# This file is part of Code_Saturne, a general-purpose CFD tool.
#
# Copyright (C) 1998-2026 EDF S.A.
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

from pathlib import Path
import subprocess as sp
import tempfile
import shutil
import os

def retrieveGitRepoForMEDFile():
    return "https://gitlab.pleiade.edf.fr/salome_cfd/vvuqe/saturne-tutorials"

class TemporaryWorkingDirectory:
    def __enter__(self):
        self._previous_cwd = Path.cwd()
        self._tempdir = tempfile.TemporaryDirectory()
        self.path = Path(self._tempdir.name)

        os.chdir(self.path)
        return self.path

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            os.chdir(self._previous_cwd)
        finally:
            self._tempdir.cleanup()

        return False
    
class AutoChangeDirectory:
    """
    For debug purpose in substitution of TemporaryWorkingDirectory to avoid cleaning effect
    """
    def __init__(self, dirname : Path):
        self._old_dir = Path( os.getcwd() )
        self._new_dir = dirname.absolute()

    @property
    def dirname(self) -> str:
        return str( self._new_dir )

    def __enter__(self):
        os.chdir( str( self._new_dir ) )
        return self._new_dir

    def __exit__(self, type, value, traceback):
        os.chdir( str( self._old_dir ) )

def retrieveMEDFile( dirName : Path ) -> Path:
    """
    Function in charge to copy MED file for the corresponding CS case in dirName.
    Default implementation retrieve it from GIT repository.
    Easy to bypass for debug purpose
    """
    
    saturne_tutorial_edf = retrieveGitRepoForMEDFile( )

    saturne_tutorial_branch_name = "main"

    with TemporaryWorkingDirectory():

        sp.check_output( [ "git", "clone", saturne_tutorial_edf ] )

        dirs = [elt for elt in Path.cwd().iterdir() if elt.is_dir()]

        if len( dirs ) != 1:

            raise RuntimeError( f"Only one dir is expected inside {os.getcwd()} after cloning" )
        
        repoDir = dirs[0]
        
        with AutoChangeDirectory( repoDir ):

            sp.check_output( [ "git", "checkout", saturne_tutorial_branch_name ] )

        dirContainingMeshes = repoDir / "01_Simple_Junction" / "MESH"

        dirs = [ elt for elt in dirContainingMeshes.iterdir() if elt.is_file() and elt.suffix == ".med" ]

        if len( dirs ) != 1:

            raise RuntimeError( f"Exactly one MED file is expected to exist inside {dirContainingMeshes}" )
        
        meshMedFile = dirs[0]

        shutil.copy( meshMedFile, dirName / meshMedFile.name )

def getResourceFileForTest( xmlCase : str ) -> Path:
    xmlFile = Path( __file__ ).absolute().parent / xmlCase
    if not xmlFile.is_file():
        raise RuntimeError( f"File {xmlCase} is expected to exist near {__file__}" )
    return xmlFile

def getOTFuncFile():
    return getResourceFileForTest( "CFD0_OT.py" )

def getCSFirstTestCase() -> Path:
    return getResourceFileForTest( "tee_junction.xml" )

def get_CS_OT_TestCase() -> Path:
    return getResourceFileForTest( "tee_junction_ot.xml" )

def OTConfFileFeeder(mainDirName : str, caseName : str, setupFileName : str) -> Path:
    """
    Function writing a OT config file in CS case for persalys execution.
    This OT config file is written in cwd / mainDirName

    :return: Path to written config file
    """
    cfgContentFileName = "openturns_study.cfg"

    cfgContent = f"""[host_parameters]
host_name = localhost
batch_manager = none
build_name = default
arch_path = default

[study_parameters]
code_name = code_saturne
study_name = {mainDirName}
ref_case = {caseName}
xmlfile = {setupFileName}
results_file = output.dat

[batch_parameters]
wall_clock = 0-00:10:00
wckey = SATURNE
nprocs = 1
number_of_nodes = 1
tasks_per_node = 1
threads_per_process = 1
distant_workdir = none
"""
    ret = Path( mainDirName ) / cfgContentFileName

    with open( str( ret ), "w" ) as f:

        f.write( cfgContent )

    return ret
    
def fillCSStudy( mainDirName : str, caseName : str, customSetupFile : Path, medFileRetriever, otConfigFeeder = None ) -> Path:
    """
    Feed current directory

    :param customSetupFile: Path to xml file
    :param MedFileRetriever: Function taking directory in input where to depose retrieved MED file of case
    :param otConfigFeeder: function responsible to write OT config file
    :return: If otConfigFeeder is not None Path to OT config file
    """

    ret = None

    setupFileName = "setup.xml"
        
    meshDir = Path( "MESH" )
    
    dataDir = Path( mainDirName ) / caseName / "DATA"
    
    sp.check_output( ["code_saturne", "create", "-s",  mainDirName, "-c", caseName ] )
    
    shutil.copy(  customSetupFile , dataDir  / setupFileName )

    medFileRetriever( Path.cwd() / mainDirName / meshDir )

    if otConfigFeeder is not None:

        ret = otConfigFeeder( mainDirName, caseName, setupFileName )

    return ret

def runCSStudy( mainDirName : str, caseName : str ):
    with AutoChangeDirectory( Path( mainDirName ) / caseName ):

        sp.check_output( [ "code_saturne" , "run" ] )

def fillAndRunCSStudy( customSetupFile : Path, medFileRetriever, otConfigFeeder = None ) -> Path:
    """
    :return: If otConfigFeeder is not None Path to OT config file
    """
    mainDirName = "simple_junction"
    caseName = "case1"
    ret = fillCSStudy( mainDirName, caseName, customSetupFile, medFileRetriever, otConfigFeeder )
    runCSStudy( mainDirName, caseName )
    return ret

def MyAssert( verdict ):
    if not verdict:
        raise RuntimeError( "MyAssert failed !" )

##################

def test0():
    with TemporaryWorkingDirectory() as tmpDir:
    
        fillAndRunCSStudy( getCSFirstTestCase( ), retrieveMEDFile, OTConfFileFeeder )

def test1( debug = False ):
    """
    To debug

    1 - Point to a local empty directory in AutoChangeDirectory constructor. Warning empty directory !
    2 - Open salome-cfd
    3 - import current module
    4 - launch current func with debug = True
    5 - Launch CFD module and load simple_junction / case1

    

    code_saturne create -s simple_junction -c case1

    ( git clone <saturne-tutorials_git_repo> && cp saturne-tutorials/12_Tee_Junction/MESH/mesh_T_junction.med simple_junction/MESH )

    cp <loc_of_cfd_extensions>/salome_cfd_extensions/test/tee_junction_ot.xml simple_junction/case1/DATA/setup.xml

    """
    def checkOutputDirs( absMainDirName : Path, nbOfOutputDirExpected : int ):
        """
        Now ready to check that CS has been launched nbEntriesInExpPlan times
        """
        import re
        pat = re.compile( "^Temp_[-]?[\d\.]+$" )
        outputDirs = [elt for elt in absMainDirName.iterdir() if elt.is_dir() and pat.match(elt.name)]

        MyAssert( len( outputDirs ) == nbOfOutputDirExpected )

        for outdir in outputDirs:
            step0 = outdir / "RESU"
            step1 = [elt for elt in step0.iterdir() if elt.is_dir()]
            MyAssert( len( step1 ) == 1 )
            step2 = step1[0] / "postprocessing" / "RESULTS_FLUID_DOMAIN.case"
            MyAssert( step2.is_file() )

    import openturns as ot
    import persalys

    nbEntriesInExpPlan = 8

    if not debug:
        CSOutputDirManager = TemporaryWorkingDirectory()
    else:
        CSOutputDirManager = AutoChangeDirectory( Path( "/path/to/empty/directory" ) )

    with CSOutputDirManager as topWorkDir:

        # First feed 
        mainDirName = "simple_junction"
        caseName = "case1"
        otConfig = fillCSStudy( mainDirName, caseName, get_CS_OT_TestCase( ), retrieveMEDFile, OTConfFileFeeder )
        #
        workDir = topWorkDir / "persalys" / "idefixresult"
        # idefixresult subdir is added only to make pydefx happy.
        ( workDir / "idefixresult" ).mkdir( parents = True, exist_ok = True )
        resultDir = topWorkDir / "idefix"
        resultDir.mkdir( parents = True, exist_ok = True )

        Study_0 = persalys.Study('Study_0')
        persalys.Study.Add(Study_0)
        dist_X0 = ot.Normal(270, 320)
        X0 = persalys.Input('X0', 0, dist_X0, '')
        Y0 = persalys.Output('Y0', '')
        Y0.setValue(0)
        inputs = [X0]
        outputs = [Y0]

        with open( getOTFuncFile(), "r" ) as f:
            code = f.read()

        dico = { "study_path" : str( topWorkDir / mainDirName ), "ot_config" : otConfig.name }

        code = code.format( **dico )
        #
        PythonModel_0 = persalys.YACSPhysicalModel('PythonModel_0', inputs, outputs, code)
        #PythonModel_0.setUseYACS(True)
        PythonModel_0.jobParameters().salome_parameters.job_name = 'idefix_job'
        PythonModel_0.jobParameters().salome_parameters.work_directory = str( workDir )
        PythonModel_0.jobParameters().salome_parameters.result_directory = str( resultDir )
        PythonModel_0.jobParameters().salome_parameters.resource_required.name = 'localhost'
        PythonModel_0.jobParameters().salome_parameters.resource_required.nb_proc = 1
        # put all entries in exp plan in one shot
        PythonModel_0.jobParameters().nb_branches = nbEntriesInExpPlan
        PythonModel_0.setDistribution('X0',  dist_X0)
        Study_0.add(PythonModel_0)
        centralTendency_0 = persalys.MonteCarloAnalysis('centralTendency_0', PythonModel_0)
        centralTendency_0.setMaximumCalls( nbEntriesInExpPlan )
        centralTendency_0.setMaximumCoefficientOfVariation(-1)
        centralTendency_0.setMaximumElapsedTime(-1)
        # put all entries in exp plan in one shot
        centralTendency_0.setBlockSize( nbEntriesInExpPlan )
        centralTendency_0.setSeed(0)
        Study_0.add(centralTendency_0)

        if debug:
            raise RuntimeError( "Normal Abort in debug mode. Just to stop b4 computing" )

        ##################################################
        centralTendency_0.run() ### <<<< GOOOOOOOOOOOOOOOO
        ##################################################

        # internally
        # persalys/idefixresult/idefixresult.csv and idefix/idefixresult/idefixresult.csv are feeded and have same content
        # Why duplication ?

        # Check is here

        checkOutputDirs( topWorkDir / mainDirName, nbEntriesInExpPlan )

        ## yes inputs are not in [ 270, 320 ] of normal
        inps = centralTendency_0.getResult().getDesignOfExperiment().getInputSample()
        inps = [ inps[elt][0] for elt in range( inps.getSize() ) ]
        
        # outputs are all set to 0. !!! Why ???
        outps = centralTendency_0.getResult().getDesignOfExperiment().getOutputSample()
        outps = [ outps[elt][0] for elt in range( outps.getSize() ) ]


if __name__ == "__main__":

    test0( )

    test1( )

