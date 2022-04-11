#!/bin/bash

BUILD_TYPE=${1:-Release}
ctest --test-dir ${BUILD_TYPE} --output-on-failure

