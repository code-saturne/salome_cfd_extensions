
if test -z ${SATURNE_ROOT_DIR} ; then
  s_saturne_ROOT_INSTALL_DIR=r"/home/NNI/BUILD/V9_CFD/code_saturne.install"
  export SATURNE_ROOT_DIR=${s_saturne_ROOT_INSTALL_DIR}
  export CS_ROOT_DIR=${s_saturne_ROOT_INSTALL_DIR}
  export LD_LIBRARY_PATH=${s_saturne_ROOT_INSTALL_DIR}/lib:$LD_LIBRARY_PATH
  export PATH=${s_saturne_ROOT_INSTALL_DIR}/bin:$PATH
  export PYTHONPATH=${s_saturne_ROOT_INSTALL_DIR}/lib/python3.9/site-packages:$PYTHONPATH
fi

s_CFDSTUDY_ROOT_INSTALL_DIR=r"/home/NNI/BUILD/MOD_SATURNE_INSTALL"
export CFDSTUDY_ROOT_DIR=${s_CFDSTUDY_ROOT_INSTALL_DIR}
export CFDSTUDY_DIR=${s_CFDSTUDY_ROOT_INSTALL_DIR}
export LD_LIBRARY_PATH=${s_CFDSTUDY_ROOT_INSTALL_DIR}/lib/salome:$LD_LIBRARY_PATH
export PYTHONPATH=${s_CFDSTUDY_ROOT_INSTALL_DIR}/bin/salome:$PYTHONPATH
export PYTHONPATH=${s_CFDSTUDY_ROOT_INSTALL_DIR}/lib/python3.8/site-packages/salome:$PYTHONPATH
export SALOME_MODULES=CFDSTUDY:$SALOME_MODULES
export SalomeAppConfig=${s_CFDSTUDY_ROOT_INSTALL_DIR}/share/salome/resources/cfdstudy:$SalomeAppConfig
