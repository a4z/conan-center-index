import os

from conans import ConanFile, CMake, tools

class DjinniSuppotLib(ConanFile):
    name = "djinni-support-lib"
    license = "Apache-2.0"
    author = "harald harald.achitz@gmail.com"
    url = "https://github.com/cross-language-cpp/"
    description = "this package contains the support lib"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
                "fPIC": [True, False],
                "target": ["JNI", "OBJC", "Auto"]
               }
    default_options = {"shared": False,
                        "fPIC": True ,
                        "target": "Auto"
                       }
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake", "cmake_find_package"

    _cmake = None

    @property
    def objc_support(self):
        if self.options.target == "Auto":
            return self.settings.os in ["iOS", "Macos"]
        else:
            return self.options.target == "OBJC"

    @property
    def jni_support(self):
        if self.options.target == "Auto":
            return self.settings.os != "iOS"
        else:
            return self.options.target == "JNI"

    # Adduse this just exists ....
    # def requirements(self):
    #     if self.jni_support:
    #         if not self.settings.os == "Android":
    #             self.requires("java_installer/9.0.0@bincrafters/stable")

    def configure(self):
        if self.settings.compiler == 'Visual Studio':
            del self.options.fPIC

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        if self.version == "pre0.2.0":
            os.rename(f"djinni-{self.version}", self._source_subfolder)
        else:
            os.rename(f"djinni-support-lib-{self.version}", self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        if not self.options.shared:
            self._cmake.definitions["DJINNI_STATIC_LIB"] = True
        self._cmake.definitions["DJINNI_WITH_OBJC"] = self.objc_support
        self._cmake.definitions["DJINNI_WITH_JNI"] = self.jni_support
        if self.jni_support:
            self._cmake.definitions["JAVA_AWT_LIBRARY"] = "NotNeeded"
            self._cmake.definitions["JAVA_AWT_INCLUDE_PATH"] = "NotNeeded"
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        # TODO , add license
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        #self.cpp_info.libdirs = ["lib"] # thats default anyway
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs = ["include",]
        # these should not be here, but as long as the generator does it ...
        self.cpp_info.includedirs.append("include/djinni")
        if self.objc_support:
            self.cpp_info.includedirs.append("include/djinni/objc")
        if self.jni_support:
            self.cpp_info.includedirs.append("include/djinni/jni")
