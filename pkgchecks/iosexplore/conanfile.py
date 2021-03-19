


# conan test tools/iosexplore/ zlib/1.2.11@ --profile ios64

import os, sys
from conans import ConanFile
from pathlib import Path

parent_path = Path(__file__).resolve().parents[1]
sys.path.append(str(parent_path))

import checkbitcode
import checkfilearch

class TestPackage(ConanFile):

    settings = "os", "arch"

    def build(self):
        pass # supress warning message

    def test(self):
        if self.settings.os != "iOS":
            return

        name = self.display_name.split()[0].split("/")[0]
        lib_paths = self.deps_cpp_info[name].lib_paths
        libs = self.deps_cpp_info[name].libs
        static_libs = list(map(lambda lib: f"lib{lib}.a", libs))

        pkg_libs = []
        for lib in static_libs:
            for libdir in lib_paths:
                libfile = f"{libdir}/{lib}"
                if Path(libfile).is_file():
                    pkg_libs.append(libfile)
                    continue

        assert len(pkg_libs) == len(libs), "not all libs found in package"

        for lib in pkg_libs:
            if self.settings.arch == "armv8":
                check_arch = "arm64"
            elif self.settings.arch == "x86_64":
                check_arch = "x86_64"
            else:
                checked_arch = False
                assert(checked_arch, f"TODO, implement arch check for {self.settings.arch}")

            assert check_arch in checkfilearch.get_file_archs(lib), f"Expected arch {self.settings.arch} ({check_arch}) not found in {lib}"
            assert checkbitcode.check_bitcode(lib, check_arch), f"Bitcode flag not found for {lib}"
