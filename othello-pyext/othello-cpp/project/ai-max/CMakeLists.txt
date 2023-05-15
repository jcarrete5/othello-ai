add_library(AIMax "")
target_sources(AIMax
    PRIVATE
        aimax.cpp
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_LIST_DIR}/aimax.h>
        $<INSTALL_INTERFACE:aimax.h>
)
target_include_directories(AIMax PUBLIC ${CMAKE_CURRENT_LIST_DIR})
target_link_libraries(AIMax PUBLIC Board)

add_executable(AIMaxTest "")
target_sources(AIMaxTest PRIVATE aimax_test.cpp)
target_include_directories(AIMaxTest PRIVATE ${CMAKE_CURRENT_LIST_DIR})
target_link_libraries(AIMaxTest PRIVATE gtest_main)
target_link_libraries(AIMaxTest PRIVATE AIMax)

gtest_discover_tests(AIMaxTest)

