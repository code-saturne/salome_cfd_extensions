
message(STATUS "cloudComPy Sphinx doc generation")

# --- Sphinx Documentation

set(RSTFILES
    index.rst
    intro.rst 
    tutorials.rst
    tutorial/coupling.rst 
    tutorial/debugging.rst 
    tutorial/saturne.rst 
    )

configure_file(conf.py.in conf.py)

SET(SPHINXOPTS )
SET(SOURCEDIR ${CMAKE_CURRENT_SOURCE_DIR})
SET(ALLSPHINXOPTS -d doctrees ${SPHINXOPTS} ${SOURCEDIR})

# install user's documentation

ADD_CUSTOM_TARGET(BUILD_HTML ALL
  COMMAND ${CMAKE_COMMAND} -E make_directory html
  COMMAND ${CMAKE_COMMAND} -E make_directory doctrees
  COMMAND ${SPHINX_EXECUTABLE} -c ${CMAKE_BINARY_DIR}/doc -b html ${ALLSPHINXOPTS} html
  DEPENDS ${RSTFILES}
  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
)

ADD_CUSTOM_TARGET(BUILD_PDF ALL
  COMMAND ${CMAKE_COMMAND} -E make_directory latex
  COMMAND ${SPHINX_EXECUTABLE} -c ${CMAKE_BINARY_DIR}/doc -b latex ${ALLSPHINXOPTS} latex
  COMMAND make -C latex all-pdf
  DEPENDS ${RSTFILES}
  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
)

INSTALL(DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/html/
  DESTINATION ${SALOME_INSTALL_DOC}/gui/CFD_tutorial
  PATTERN ".buildinfo" EXCLUDE
)

INSTALL(FILES ${CMAKE_CURRENT_BINARY_DIR}/latex/CFDSTUDY.pdf DESTINATION ${SALOME_INSTALL_DOC}/gui/CFD_tutorial)
