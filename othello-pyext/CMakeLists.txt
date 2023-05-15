cmake_minimum_required(VERSION 3.15.0)

project(OthelloPyExt)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

add_subdirectory(external)

pybind11_add_module(othello_cpp
    main.cpp
)

add_subdirectory(othello-cpp)
target_link_libraries(othello_cpp PRIVATE Board)
target_link_libraries(othello_cpp PRIVATE AIMax)

target_compile_definitions(othello_cpp PRIVATE
    VERSION_INFO=${EXAMPLE_VERSION_INFO}
)

