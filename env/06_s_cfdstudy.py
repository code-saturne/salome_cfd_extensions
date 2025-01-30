# syrthes installation on base salome.
# Associated syrthes code and module installs may be outside of base salome install tree.

import os.path
import sys

def init(context, root_dir):
    python_version = "%d.%d" % (sys.version_info.major, sys.version_info.minor)
    pythondir_rel = os.path.join(r"lib", r"python" + python_version, r"site-packages")

    from os import getenv
    s = getenv(r"CS_ROOT_DIR")
    if s is None:
        s_saturne_ROOT_INSTALL_DIR=r"/home/NNI/BUILD/V9_CFD/code_saturne.install"
        context.setVariable(r"CS_ROOT_DIR", s_saturne_ROOT_INSTALL_DIR, overwrite=True)
        context.addToLdLibraryPath(os.path.join(s_saturne_ROOT_INSTALL_DIR, r"lib"))
        context.addToPath(os.path.join(s_saturne_ROOT_INSTALL_DIR, r"bin"))
        context.addToPythonPath(os.path.join(s_saturne_ROOT_INSTALL_DIR, pythondir_rel))

    s_CFDSTUDY_ROOT_INSTALL_DIR=r"/home/NNI/BUILD/MOD_SATURNE_INSTALL"
    context.setVariable(r"CFDSTUDY_ROOT_DIR", os.path.join(s_CFDSTUDY_ROOT_INSTALL_DIR, r""), overwrite=True)
    context.setVariable(r"CFDSTUDY_DIR", os.path.join(s_CFDSTUDY_ROOT_INSTALL_DIR, r""), overwrite=True)
    context.addToLdLibraryPath(os.path.join(s_CFDSTUDY_ROOT_INSTALL_DIR, r"lib", r"salome"))
    context.addToPath(os.path.join(s_CFDSTUDY_ROOT_INSTALL_DIR, r"bin", r"salome"))
    context.addToPythonPath(os.path.join(s_CFDSTUDY_ROOT_INSTALL_DIR, r"bin", r"salome"))
    context.addToPythonPath(os.path.join(s_CFDSTUDY_ROOT_INSTALL_DIR, pythondir_rel, r"salome"))
    os.environ["SALOME_MODULES"] = os.getenv("SALOME_MODULES") + "," + "CFDSTUDY"
    context.appendVariable(r"SalomeAppConfig", os.path.join(s_CFDSTUDY_ROOT_INSTALL_DIR, r"share/salome/resources/cfdstudy"))
