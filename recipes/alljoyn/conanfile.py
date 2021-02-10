import os

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

class Alljoyn(ConanFile):
    name = "alljoyn"
 #   version = "0.16.10"
    license = "Apache-2.0"
    author = "harald harald.achitz@electrolux.com"
    description = "this is the alljoyn build we need"
    settings = "os" , "compiler", "build_type", "arch"
    generators = "scons"
    build_requires = "scons/3.1.2"
    short_paths = True

    def source(self):
        # TODO get downloads of the source, the git clone is not optimal

        # get back the original names,
        core_alljoyn = "ssh://git@bitbucket.edp.electrolux.io/sdk/alljoyn-core.git"
        service_base = "ssh://git@bitbucket.edp.electrolux.io/sdk/alljoyn-base.git"

        if not os.path.exists("core"):
            os.mkdir("core")
        if not os.path.exists("services"):
            os.mkdir("services")

        # TODO, will we stay on dev branch for ever ?
        self.run(f"git clone --depth 1 --branch next1 {core_alljoyn} core/alljoyn")
        self.run(f"git clone --depth 1 --branch next1 {service_base} services/base")


    def build_osx_for(self, sdk):

        # This is the greatest brainfuck ever seen, no wonder this project is dead
        if sdk in ["iphoneos","iphonesimulator"]:
            platform_name = "iOS"
            #spec = "OS=iOS CPU=universal"
            if self.settings.arch == "armv8":
                spec = "OS=iOS CPU={}".format("arm64")
            else:
                spec = "OS=iOS CPU={}".format(self.settings.arch)

            if sdk ==  "iphonesimulator":
                platform_name = "iphonesimulator"
        else:
            platform_name = sdk
            spec = "CPU=x86_64"

        # CONFIGURATION=release not needed for macosx, see this has been done by different developers without any common concept ;-)
        env_settings= f"CONFIGURATION={self.settings.build_type} PLATFORM_NAME={platform_name} SDKROOT={tools.XCRun(self.settings, sdk).sdk_path} BUILD_SERVICES_SAMPLES=off"

        work_dir = f"-C {self.source_folder}/core/alljoyn"
        jobs = f"--jobs {tools.cpu_count()}"

        #scons_call = f"scons {work_dir} {jobs} {spec} BINDINGS=cpp BR=on WS=off BT=off ICE=off VARIANT=Release CRYPTO=builtin DOCS=none SERVICES=about,notification,controlpanel,config,onboarding"
        scons_call = f"scons {work_dir} {jobs} {spec} BINDINGS='cpp' BR=on WS=off BT=off ICE=off VARIANT={self.settings.build_type} CRYPTO=builtin DOCS=none SERVICES='about,notification,controlpanel,config,onboarding'"
        self.output.info(f"{env_settings} {scons_call}")

        self.run(f"{env_settings} {scons_call}")

    def build_android(self):

        if self.settings.arch == "armv7":
            spec = "OS=android CPU=arm"
        elif self.settings.arch == "armv8":
            spec = "OS=android CPU=arm64"
        elif self.settings.arch == "x86_64":
            spec = "OS=android CPU=x86_64"
        elif self.settings.arch == "x86":
            spec = "OS=android CPU=x86"
        else:
            raise ConanInvalidConfiguration(f" Uknowown arch {self.settings.arch} for Andriod build")

        # NDK_ROOT must come from the ndk conan package, or from somewhere else
        # use the conan package, by using the right profile
        env_settings = f"ANDROID_NDK={os.environ['ANDROID_NDK_HOME']}"

        work_dir = f"-C {self.source_folder}/core/alljoyn"
        jobs = f"--jobs {tools.cpu_count()}"

        scons_call = f"scons {work_dir} {jobs} {spec} BINDINGS='cpp' BR=on WS=off BT=off ICE=off VARIANT={self.settings.build_type} CRYPTO=builtin DOCS=none SERVICES='about,notification,controlpanel,config,onboarding'"
        self.output.info(f"{scons_call}")

        self.run(f"{env_settings} {scons_call}")

    def build_linux(self):
        # I think this line is not needed at all, but it does not harm ....
        env_settings= f"CONFIGURATION={self.settings.build_type} PLATFORM_NAME=Linux BUILD_SERVICES_SAMPLES=off"

        work_dir = f"-C {self.source_folder}/core/alljoyn"
        jobs = f"--jobs {tools.cpu_count()}"
        spec = "OS=linux CPU=x86_64"

        scons_call = f"scons {work_dir} {jobs} {spec} BINDINGS='cpp' BR=on WS=off BT=off ICE=off VARIANT={self.settings.build_type} CRYPTO=builtin DOCS=none SERVICES='about,notification,controlpanel,config,onboarding'"
        self.output.info(f"{env_settings} {scons_call}")

        self.run(f"{env_settings} {scons_call}")

    def build_windows(self):
        # I think this line is not needed at all, but it does not harm ....
        env_settings= f"CONFIGURATION={self.settings.build_type} PLATFORM_NAME=Windows BUILD_SERVICES_SAMPLES=off"

        work_dir = f"-C {self.source_folder}/core/alljoyn"
        jobs = f"--jobs {tools.cpu_count()}"
        spec = "OS=win10 CPU=x86_64 MSVC_VERSION=14.2 CPPDEFINES=QCC_OS_WINDOWS"  # TODO , 14.2 should not be hardcoded

        # for openssl crypto, I need to figure out how to transport this into scons
        # internal crypto does not exist on windows
        #scons_call = f"scons {work_dir} {jobs} {spec} BINDINGS='cpp' BR=on WS=off BT=off ICE=off VARIANT={self.settings.build_type} CRYPTO=openssl DOCS=none SERVICES='about,notification,controlpanel,config,onboarding'"
        scons_call = f"scons {work_dir} {jobs} {spec} BINDINGS=cpp BR=on WS=off BT=off ICE=off VARIANT={self.settings.build_type} CRYPTO=cng DOCS=none SERVICES=about,notification,controlpanel,config,onboarding BUILD_SERVICES_SAMPLES=off"
        # no crypto works of cause also
        #scons_call = f"scons {work_dir} {jobs} {spec} BINDINGS='cpp' BR=on WS=off BT=off ICE=off VARIANT={self.settings.build_type} DOCS=none SERVICES='about,notification,controlpanel,config,onboarding'"
        self.output.info(f"{env_settings} {scons_call}")

        self.run(f"{scons_call}")


    def build(self):
        # TODO make VARIANT and CRYPTO to an option
        if self.settings.os  == "Macos":
            self.build_osx_for("macosx")
        elif self.settings.os  == "iOS":
            # if self.options["ios-cmake"].ios_target in ["OS", "OS64"]:
            #     self.build_osx_for("iphoneos")
            # elif self.options["ios-cmake"].ios_target in ["SIMULATOR", "SIMULATOR64"]:
            #     self.build_osx_for("iphonesimulator")
            # elif self.options["ios-cmake"].ios_target == "OS64COMBINED":
            #     raise ConanInvalidConfiguration(f"OS64COMBINED build not supported yet")
            if self.settings.arch == "x86_64":
                self.build_osx_for("iphonesimulator")
            else:
                self.build_osx_for("iphoneos")

        elif self.settings.os  == "Android":
            self.build_android()

        elif self.settings.os  == "Linux":
            self.build_linux()

        elif self.settings.os  == "Windows":
            self.build_windows()

        else:
            raise ConanInvalidConfiguration(f" os {self.settings.os} not supported yet")


    def package(self):

        build_dir = f"{self.source_folder}/core/alljoyn/build"
        build_type = str(self.settings.build_type).lower()
        # this is total not DRY, make a function that returns Macos_macos, Macos_ios, Macos_simulator Macos_android to get rid of this nesting
        if self.settings.os  == "Macos":
            install_dir = f"{build_dir}/darwin/x86_64/{build_type}/dist"
        elif self.settings.os  == "iOS":
            # if self.options["ios-cmake"].ios_target in ["OS", "OS64"]:
            #     install_dir = f"{build_dir}/iOS/universal/iOS/{build_type}/dist"
            # elif self.options["ios-cmake"].ios_target in ["SIMULATOR", "SIMULATOR64"]:
            #     install_dir = f"{build_dir}/iOS/universal/iphonesimulator/{build_type}/dist"
            # elif self.options["ios-cmake"].ios_target == "OS64COMBINED":
            #     raise ConanInvalidConfiguration(f"OS64COMBINED build not supported yet")
            if self.settings.arch == "x86_64":
                install_dir = f"{build_dir}/iOS/{self.settings.arch}/iphonesimulator/{build_type}/dist"
            else:
                archdir = self.settings.arch
                if self.settings.arch == "armv8":
                    archdir = "arm64"
                install_dir = f"{build_dir}/iOS/{archdir}/iOS/{build_type}/dist"

        elif self.settings.os  == "Android":
            if self.settings.arch == "armv7":
                install_dir = f"{build_dir}/android/arm/{build_type}/dist"
            elif self.settings.arch == "armv8":
                install_dir = f"{build_dir}/android/arm64/{build_type}/dist"
            elif self.settings.arch == "x86_64":
                install_dir = f"{build_dir}/android/x86_64/{build_type}/dist"
            elif self.settings.arch == "x86":
                install_dir = f"{build_dir}/android/x86/{build_type}/dist"
            else:
                raise ConanInvalidConfiguration(f" Unknown arch {self.settings.arch} for Android")

        elif self.settings.os == "Linux":
            install_dir = f"{build_dir}/linux/x86_64/{build_type}/dist"

        elif self.settings.os == "Windows":
            install_dir = f"{build_dir}/win10/x86_64/{build_type}/dist"

        else:
            raise ConanInvalidConfiguration(f" os {self.settings.os} not supported yet")

        lib_pattern = "*.lib" if self.settings.os == "Windows" else "*.a"

        self.copy (pattern=lib_pattern, dst="lib", src=install_dir, keep_path=False)

        self.copy (pattern="*.h", dst="include", src=f"{install_dir}/controlpanel/inc", keep_path=True)
        self.copy (pattern="*.h", dst="include", src=f"{install_dir}/cpp/inc", keep_path=True)
        self.copy (pattern="*.h", dst="include", src=f"{install_dir}/notification/inc", keep_path=True)
        self.copy (pattern="*.h", dst="include", src=f"{install_dir}/onboarding/inc", keep_path=True)
        self.copy (pattern="*.h", dst="include", src=f"{install_dir}/services_common/inc", keep_path=True)


    def package_info(self):
        # self.cpp_info.names["cmake_find_package"] = "Alljoyn"
        # self.cpp_info.names["cmake_find_package_multi"] = "Alljoyn"
        self.cpp_info.libs = ["ajrouter",
                            "alljoyn",
                            "alljoyn_about",
                            "alljoyn_config",
                            "alljoyn_controlpanel",
                            "alljoyn_notification",
                            "alljoyn_onboarding",
                            "alljoyn_services_common"]

        if self.settings.os == "Windows":
            self.cpp_info.cxxflags.append("QCC_OS_WINDOWS")
