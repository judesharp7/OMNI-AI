cmake_minimum_required(VERSION 3.14)
project(omni_kernel LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# ── Shared library (imported by Python via ctypes) ──────────────
add_library(omni_kernel SHARED omni_kernel.cpp)

if(MSVC)
    target_compile_options(omni_kernel PRIVATE /O2 /EHsc /W4)
else()
    target_compile_options(omni_kernel PRIVATE
        -O3 -march=native -Wall -Wextra -fPIC)
    target_link_libraries(omni_kernel PRIVATE pthread)
endif()

# ── Self-test executable ────────────────────────────────────────
add_executable(omni_kernel_test omni_kernel.cpp)
target_compile_definitions(omni_kernel_test PRIVATE OMNI_KERNEL_TEST)

if(MSVC)
    target_compile_options(omni_kernel_test PRIVATE /O2 /EHsc)
else()
    target_compile_options(omni_kernel_test PRIVATE -O2 -march=native)
    target_link_libraries(omni_kernel_test PRIVATE pthread)
endif()

# ── Install rules ───────────────────────────────────────────────
install(TARGETS omni_kernel
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin)
