cmake_minimum_required(VERSION 3.15.0)

project(Othello VERSION 0.1.0)
set(CMAKE_CXX_STANDARD 20)

add_compile_definitions(
  $<$<CONFIG:DEBUG>:DEBUG>
)

include(CPack)
set(CPACK_PROJECT_NAME ${PROJECT_NAME})
set(CPACK_PROJECT_VERSION ${PROJECT_VERSION})

include(CTest)

include(FetchContent)
FetchContent_Declare(googletest
    GIT_REPOSITORY https://github.com/google/googletest.git
    GIT_TAG release-1.11.0
)
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE) # For Windows: Prevent overriding the parent project's compiler/linker settings
FetchContent_MakeAvailable(googletest)
include(GoogleTest)

add_subdirectory(project)

