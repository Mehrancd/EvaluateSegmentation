cmake_minimum_required(VERSION 3.13.4)

project(EvaluationSegmentation)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://www.slicer.org/wiki/Documentation/Nightly/Extensions/EvaluationSegmentation")
set(EXTENSION_CATEGORY "Examples")
set(EXTENSION_CONTRIBUTORS "Mehran Azimbagirad (LATIM)")
set(EXTENSION_DESCRIPTION "This is an example of a simple extension")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/EvaluationSegmentation.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/EvaluationSegmentation/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(EvaluateSegmentation)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
