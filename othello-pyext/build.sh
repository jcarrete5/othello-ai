#!/bin/bash

BUILD_TYPE=${1:-Release}
mkdir $BUILD_TYPE 2>/dev/null
pushd $BUILD_TYPE

CMAKE_OPTIONS="-DCMAKE_BUILD_TYPE=${BUILD_TYPE}"

if cmake .. ${CMAKE_OPTIONS} ; then
    echo "CMake finished"
else
    exit $?
fi
if cmake --build . && cmake --install . --prefix . ; then
    echo "Build finished"
else
    exit $?
fi

cp compile_commands.json .. 2>/dev/null

popd
