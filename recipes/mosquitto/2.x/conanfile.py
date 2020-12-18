import os

from conans import ConanFile, CMake, tools


class Mosquitto(ConanFile):
    name = "mosquitto"
    license = "EPL-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://mosquitto.org"
    description = """Eclipse Mosquitto MQTT library, broker and more"""
    topics = ("MQTT", "IoT", "eclipse")
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
                "with_ssl": [True, False],
                "clients": [True, False],
                "broker": [True, False],
                "apps": [True, False],
                "plugins": [True, False],
                "with_cjson": [True, False],
            }
    default_options = {"shared": False,
                        "with_ssl": True,
                        "clients": False,
                        "broker": False,
                        "apps": False,
                        "plugins": False,
                        "with_cjson": False
    }

    _cmake = None


    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _ssl_on(self):
        if self.settings.os == "Windows":
            return False # for the moment it is like that
            # however, there might be cygwin and others where it even works on Windows for the moment ...
        return self.options.with_ssl

    def requirements(self):
        if self._ssl_on:
            self.requires("openssl/1.1.1i")
        if self.options.with_cjson:
            self.requires("cjson/1.7.14")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name.replace("-", ".") + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["WITH_TLS"] = self._ssl_on
        self._cmake.definitions["WITH_CLIENTS"] = self.options.clients
        self._cmake.definitions["WITH_BROKER"] = self.options.broker
        self._cmake.definitions["WITH_APPS"] = self.options.apps
        self._cmake.definitions["WITH_PLUGINS"] = self.options.plugins
        self._cmake.definitions["DOCUMENTATION"] = False
        if self._ssl_on:
            self._cmake.definitions["OPENSSL_SEARCH_PATH"] = self.deps_cpp_info["openssl"].rootpath.replace("\\", "/")
            self._cmake.definitions["OPENSSL_ROOT_DIR"] = self.deps_cpp_info["openssl"].rootpath.replace("\\", "/")
        self._cmake.configure(source_folder=self._source_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("edl-v10", src=self._source_subfolder, dst="licenses")
        self.copy("edl-v20", src=self._source_subfolder, dst="licenses")
        self.copy("LICENSE.txt", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib","pkgconfig"))

    def package_info(self):
        #self.cpp_info.libdirs = ["lib"] # thats default anyway
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs = ["include",]

