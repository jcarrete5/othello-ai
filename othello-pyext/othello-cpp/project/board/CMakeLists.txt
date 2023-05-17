add_library(Board "")
target_compile_definitions(Board PRIVATE $<$<CONFIG:DEBUG>:DEBUG>)
target_sources(Board PRIVATE board.cpp bit_board.cpp)
target_include_directories(Board PUBLIC ${CMAKE_CURRENT_LIST_DIR})

add_executable(BoardTest "")
target_sources(BoardTest PRIVATE bit_board_test.cpp board_test.cpp)
target_include_directories(BoardTest PRIVATE ${CMAKE_CURRENT_LIST_DIR})
target_link_libraries(BoardTest PRIVATE gtest_main)
target_link_libraries(BoardTest PRIVATE Board)

gtest_discover_tests(BoardTest)

