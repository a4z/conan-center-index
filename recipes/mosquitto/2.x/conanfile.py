import os

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.31.0"


class Mosquitto(ConanFile):
    name = "mosquitto"
    license = "EPL-2.0", "EPL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://mosquitto.org"
    description = """Eclipse Mosquitto MQTT library, broker and more"""
    topics = ("MQTT", "IoT", "eclipse")
    exports_sources = "CMakeLists.txt"
    generators = "cmake" , "cmake_find"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
                "with_tls": [True, False],
                "clients": [True, False],
                "broker": [True, False],
                "apps": [True, False],
                "plugins": [True, False],
                "with_cjson": [True, False],
                "build_cpp": [True, False],
                "with_websockets": [True, False],
            }
    default_options = {"shared": False,
                        "with_tls": True,
                        "clients": False,
                        "broker": False,
                        "apps": False,
                        "plugins": False,  # TODO, there is some logic, just enabling plugin does not work, needs also something else
                        "with_cjson": False ,
                        "build_cpp": True ,
                        "with_websockets": False
    }
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake", "cmake_find_package"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if not self.options.clients and not self.options.clients:
            del self.options.cjson
        if not self.options.broker:
            del self.options.websockets
        if not self.options.build_cpp:
            del self.settings.compiler.libcxx
            del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.with_tls:
            self.requires("openssl/1.1.1i")
        if self.options.get_safe("cjson"):
            self.requires("cjson/1.7.14")
        if self.options.get_safe("websockets"):
            self.requires("libwebsockets/4.1.6")

    def configure(self):
        if self.settings.compiler == "Visual Studio" and "MT" in self.settings.compiler.runtime:
            raise ConanInvalidConfiguration("Visual Studio build for any MT runtime is not supported")
        if self.options.with_cjson: # see _configure_cmake for the reason
            raise ConanInvalidConfiguration("Option with_cjson not yet supported")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name.replace("-", ".") + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["WITH_THREADING"] = self.settings.os != "Windows"
        self._cmake.definitions["WITH_PIC"] = self.options.get_safe("fPIC", False)
        self._cmake.definitions["WITH_STATIC_LIBRARIES"] = not self.options.shared
        self._cmake.definitions["WITH_TLS"] = self.options.with_tls
        self._cmake.definitions["WITH_CLIENTS"] = self.options.clients
        self._cmake.definitions["WITH_BROKER"] = self.options.broker
        self._cmake.definitions["WITH_APPS"] = self.options.apps
        self._cmake.definitions["WITH_PLUGINS"] = False
        self._cmake.definitions["WITH_LIB_CPP"] = self.options.build_cpp
        self._cmake.definitions["WITH_WEBSOCKETS"] = self.options.get_safe("websockets", False)
        self._cmake.definitions["STATIC_WEBSOCKETS"] = self.options.get_safe("websockets", False) and not self.options["libwebsockets"].shared
        self._cmake.definitions["DOCUMENTATION"] = False
        self._cmake.definitions["CMAKE_INSTALL_SYSCONFDIR"] = os.path.join(self.package_folder, "res").replace("\\", "/")
        self._cmake.configure(build_folder=self._build_subfolder)
        if self.options.with_tls:
            self._cmake.definitions["OPENSSL_SEARCH_PATH"] = self.deps_cpp_info["openssl"].rootpath.replace("\\", "/")
            self._cmake.definitions["OPENSSL_ROOT_DIR"] = self.deps_cpp_info["openssl"].rootpath.replace("\\", "/")
        return self._cmake

    # def _patch_sources(self):
    #     tools.replace_in_file(os.path.join(self._source_subfolder, "client", "CMakeLists.txt"), "static)", "static ${CONAN_LIBS})")
    #     tools.replace_in_file(os.path.join(self._source_subfolder, "client", "CMakeLists.txt"), "quitto)", "quitto ${CONAN_LIBS})")
    #     tools.replace_in_file(os.path.join(self._source_subfolder, "apps", "mosquitto_ctrl", "CMakeLists.txt"), "static)", "static ${CONAN_LIBS})")
    #     tools.replace_in_file(os.path.join(self._source_subfolder, "apps", "mosquitto_ctrl", "CMakeLists.txt"), "quitto)", "quitto ${CONAN_LIBS})")
    #     tools.replace_in_file(os.path.join(self._source_subfolder, "apps", "mosquitto_passwd", "CMakeLists.txt"), "OPENSSL_LIBRARIES", "CONAN_LIBS")
    #     tools.replace_in_file(os.path.join(self._source_subfolder, "src", "CMakeLists.txt"), "MOSQ_LIBS", "CONAN_LIBS")

    def _patch_sources(self):
        if self.settings.os == "Windows":
            if self.options.with_tls:
                tools.replace_in_file(os.path.join(self._source_subfolder, "lib", "CMakeLists.txt"),
                                    "${OPENSSL_LIBRARIES}",
                                    "${OPENSSL_LIBRARIES} crypt32")
                tools.replace_in_file(os.path.join(self._source_subfolder, "src", "CMakeLists.txt"),
                                    "${OPENSSL_LIBRARIES}",
                                    "${OPENSSL_LIBRARIES} crypt32")
                # This is so inconsequent, there is ws2_32 meanwhile in the build, but forgotten here
                tools.replace_in_file(os.path.join(self._source_subfolder, "apps", "mosquitto_passwd" ,"CMakeLists.txt"),
                                    "${OPENSSL_LIBRARIES}",
                                    "${OPENSSL_LIBRARIES} ws2_32 crypt32")

        tools.replace_in_file(os.path.join(self._source_subfolder, "lib", "CMakeLists.txt"),
                            "install(TARGETS libmosquitto RUNTIME DESTINATION \"${CMAKE_INSTALL_BINDIR}\" LIBRARY DESTINATION \"${CMAKE_INSTALL_LIBDIR}\")",
                            "install(TARGETS libmosquitto RUNTIME DESTINATION \"${CMAKE_INSTALL_BINDIR}\" LIBRARY DESTINATION \"${CMAKE_INSTALL_LIBDIR}\" ARCHIVE DESTINATION \"${CMAKE_INSTALL_LIBDIR}\")")
        tools.replace_in_file(os.path.join(self._source_subfolder, "lib", "cpp", "CMakeLists.txt"),
                            "install(TARGETS mosquittopp RUNTIME DESTINATION \"${CMAKE_INSTALL_BINDIR}\" LIBRARY DESTINATION \"${CMAKE_INSTALL_LIBDIR}\")",
                            "install(TARGETS mosquittopp RUNTIME DESTINATION \"${CMAKE_INSTALL_BINDIR}\" LIBRARY DESTINATION \"${CMAKE_INSTALL_LIBDIR}\" ARCHIVE DESTINATION \"${CMAKE_INSTALL_LIBDIR}\")")


    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("edl-v10", src=self._source_subfolder, dst="licenses")
        self.copy("edl-v20", src=self._source_subfolder, dst="licenses")
        self.copy("LICENSE.txt", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "res"), "*.example")
        if not self.options.shared:
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.so*")
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.dylib")
            tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "*.dll")

        tools.rmdir(os.path.join(self.package_folder, "lib","pkgconfig"))
        if not self.options.shared:
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.so*")
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.dll*")
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.dylib*")

    def package_info(self):
        libsuffix = "" if self.options.shared else "_static"
        self.cpp_info.components["libmosquitto"].names["pkg_config"] = "libmosquitto"
        self.cpp_info.components["libmosquitto"].libs = ["mosquitto" + libsuffix]
        self.cpp_info.components["libmosquitto"].requires = ["openssl::openssl"]
        if self.settings.os == "Linux":
            self.cpp_info.components["libmosquitto"].system_libs = ["pthread", "m"]
        elif self.settings.os == "Windows":
            self.cpp_info.components["libmosquitto"].system_libs = ["ws2_32"]

        if self.options.build_cpp:
            self.cpp_info.components["libmosquittopp"].names["pkg_config"] = "libmosquittopp"
            self.cpp_info.components["libmosquittopp"].libs = ["mosquittopp" + libsuffix]
            self.cpp_info.components["libmosquittopp"].requires = ["libmosquitto"]
            if self.settings.os == "Linux":
                self.cpp_info.components["libmosquittopp"].system_libs = ["pthread", "m"]
            elif self.settings.os == "Windows":
                self.cpp_info.components["libmosquittopp"].system_libs = ["ws2_32"]

        if self.options.broker:
            self.cpp_info.components["broker"].libdirs = []
            self.cpp_info.components["broker"].include_dirs = []
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH env var with : {}".format(bin_path))
            self.env_info.PATH.append(bin_path)
            if self.options.websockets:
                self.cpp_info.components["broker"].requires.append("libwebsockets::libwebsockets")
            if self.settings.os == "Linux":
                self.cpp_info.components["broker"].system_libs = ["pthread", "m"]
            elif self.settings.os == "Windows":
                self.cpp_info.components["broker"].system_libs = ["ws2_32"]

        for option in ["apps", "clients"]:
            if self.options.get_safe(option):
                self.cpp_info.components[option].libdirs = []
                self.cpp_info.components[option].include_dirs = []
                bin_path = os.path.join(self.package_folder, "bin")
                self.output.info("Appending PATH env var with : {}".format(bin_path))
                self.env_info.PATH.append(bin_path)
                self.cpp_info.components[option].requires = ["openssl::openssl", "libmosquitto"]
                if self.options.cjson:
                    self.cpp_info.components[option].requires.append("cjson::cjson")
