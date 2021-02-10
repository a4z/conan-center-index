import os

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

class Djinni(ConanFile):
    name = "djinni-generator"
    license = "Apache-2.0"
    author = "harald.achitz@gmail.com"
    url = "https://github.com/cross-language-cpp/djinni-generator"
    description = "This package contains the code generator"
    settings = "os",  "arch"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(f"djinni-{self.version}", self._source_subfolder)

    def build(self):
        os.chdir(self._source_subfolder)
        self.run("make djinni_standalone")

    def package(self):
        self.copy(f"{self._source_subfolder}/src/target/bin/djinni", dst="bin", keep_path=False)

    def package_info(self):
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))

