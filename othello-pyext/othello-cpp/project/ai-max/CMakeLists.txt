add_library(AIMax "")
target_compile_definitions(AIMax PRIVATE $<$<CONFIG:DEBUG>:DEBUG>)
target_sources(AIMax PRIVATE aimax.cpp)
target_include_directories(AIMax PUBLIC ${CMAKE_CURRENT_LIST_DIR})
target_link_libraries(AIMax PUBLIC Board)

add_executable(AIMaxTest "")
target_sources(AIMaxTest PRIVATE aimax_test.cpp)
target_include_directories(AIMaxTest PRIVATE ${CMAKE_CURRENT_LIST_DIR})
target_link_libraries(AIMaxTest PRIVATE gtest_main)
target_link_libraries(AIMaxTest PRIVATE AIMax)

gtest_discover_tests(AIMaxTest)

