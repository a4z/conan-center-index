import os

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

class Djinni(ConanFile):
    name = "djinni-generator"
    license = "Apache-2.0"
    author = "harald.achitz@gmail.com"
    url = "https://github.com/cross-language-cpp/djinni-generator"
    description = "This package contains the code generator"
    settings = "os", "arch"


    def source(self):
        filename = os.path.basename(self.conan_data["sources"][self.version]["url"])
        tools.download(filename=filename, **self.conan_data["sources"][self.version])

    def build(self):
        pass # avoid warning for missing build steps

    def package(self):
        if tools.detected_os() == "Windows":
            os.rename('djinni','djinni.bat')
            self.copy("djinni.bat", dst="bin", keep_path=False)
        else:
            self.copy("djinni", dst="bin", keep_path=False)
            executable = os.path.join(self.package_folder, "bin", "djinni")
            os.chmod(executable, os.stat(executable).st_mode | 0o111)

    def package_info(self):
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))

