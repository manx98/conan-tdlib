cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

find_package(Td 1.8.25 REQUIRED)
find_package(OpenSSL REQUIRED)
find_package(ZLIB REQUIRED)
add_executable(example src/example.cpp)
target_include_directories(example PRIVATE Td_INCLUDE_DIR)
target_link_libraries(example PRIVATE Td::TdStatic ${OPENSSL_LIBRARIES})
