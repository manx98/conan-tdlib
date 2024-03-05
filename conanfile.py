import os.path

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import get, replace_in_file, rmdir
from conan.tools.microsoft import is_msvc
from collections import namedtuple


class TDLibRecipe(ConanFile):
    name = "tdlib"
    version = "1.8.25"
    package_type = "library"

    # Optional metadata
    license = "BSL-1.0 license"
    homepage = "https://core.telegram.org/tdlib"
    url = "https://github.com/tdlib/td"
    description = ("TDLib (Telegram Database library) is a cross-platform library for building Telegram clients. It "
                   "can be easily used from almost any programming language.")
    topics = ("telegram", "cross-platform")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = {
        "shared": False
    }

    # Sources are located in the same place as this recipe, copy them to the recipe
    # exports_sources = "CMakeLists.txt", "src/*", "include/*"
    _TdComponent = namedtuple("_TdComponent",
                              ("name", "dependencies", "external_dependencies", "is_lib"))
    _td_component_tree = {
        "tdclient": _TdComponent("TdStatic", ["tdapi", "tdutils", "tdcore"], [], True),
        "tdjson": _TdComponent("TdJson", ["tdjson_private"], [], True),
        "tdjson_static": _TdComponent("TdJsonStatic", ["tdjson_private"], [], True),
        "tdapi": _TdComponent(None, ["tdutils"], [], True),
        "tdutils": _TdComponent(None, [], ["openssl::openssl"], True),
        "tdcore": _TdComponent(None, ["tdapi", "tdactor", "tdutils", "tdnet", "tddb"], ["zlib::zlib", "openssl::openssl"], True),
        "tdjson_private": _TdComponent(None, ["tdclient", "tdutils"], [], True),
        "tdactor": _TdComponent(None, ["tdutils"], [], True),
        "tdnet": _TdComponent(None, ["tdutils", "tdactor"], ["zlib::zlib", "openssl::openssl"], True),
        "tddb": _TdComponent(None, ["tdactor", "tdutils", "tdsqlite"], [], True),
        "tdsqlite": _TdComponent(None, [], ["zlib::zlib", "openssl::openssl"], True)
    }

    def source(self):
        get(self, **self.conan_data["sources"][self.version])
        root_cmake_list = os.path.join(self.source_path, "CMakeLists.txt")
        replace_in_file(self, root_cmake_list, "if (OPENSSL_FOUND)", """if (OPENSSL_FOUND)
  get_filename_component(OPENSSL_LIB_DIR ${OPENSSL_INCLUDE_DIR} DIRECTORY)
  link_directories("${OPENSSL_LIB_DIR}/lib")""")
        replace_in_file(self, root_cmake_list, "add_subdirectory(benchmark)", "#add_subdirectory(benchmark)")

    def validate(self):
        pass

    def config_options(self):
        pass

    def configure(self):
        pass

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Td")
        self.cpp_info.set_property("cmake_target_name", "Td")
        self.cpp_info.filenames["cmake_find_package"] = "Td"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Td"
        self.cpp_info.names["cmake_find_package"] = "Td"
        self.cpp_info.names["cmake_find_package_multi"] = "Td"
        for comp_name, comp in self._td_component_tree.items():
            conan_component = f"td_{comp_name.lower()}"
            requires = [f"td_{dependency.lower()}" for dependency in comp.dependencies] + comp.external_dependencies
            if comp.name:
                self.cpp_info.components[conan_component].set_property("cmake_target_name", f"Td::{comp.name}")
                self.cpp_info.components[conan_component].set_property("cmake_file_name", comp.name)
                self.cpp_info.components[conan_component].names["cmake_find_package"] = comp.name
                self.cpp_info.components[conan_component].names["cmake_find_package_multi"] = comp.name
            if comp.is_lib:
                self.cpp_info.components[conan_component].libs = [comp_name]
            self.cpp_info.components[conan_component].requires = requires
        if self.settings.os == "Windows":
            mswsock = "Mswsock" if is_msvc(self) else "mswsock"
            crypt32 = "Crypt32" if is_msvc(self) else "crypt32"
            self.cpp_info.components["td_tdutils"].system_libs.extend([crypt32, "ws2_32", mswsock, "Normaliz", "psapi", "shell32"])
            self.cpp_info.components["td_tdcore"].system_libs.extend([crypt32, "ws2_32", mswsock])
            self.cpp_info.components["tdsqlite"].system_libs.extend([crypt32, "ws2_32", mswsock])
            self.cpp_info.components["tdnet"].system_libs.extend([crypt32, "ws2_32", mswsock])
            self.cpp_info.components["tdjson"].system_libs.extend([crypt32, "ws2_32", mswsock])
            self.cpp_info.components["tdjson_static"].system_libs.extend([crypt32, "ws2_32", mswsock])

    def requirements(self):
        requirements = self.conan_data.get('requirements', [])
        for requirement in requirements:
            self.requires(requirement)
