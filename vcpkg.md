# VCpkg Notes

The C++ package manager that we will need to use going forward.

## Links

- [Shell setup](https://learn.microsoft.com/en-us/vcpkg/get_started/get-started-packaging?pivots=shell-bash)
- [Manifests](https://learn.microsoft.com/en-us/vcpkg/reference/vcpkg-json)
- [Overlay Ports](https://learn.microsoft.com/en-us/vcpkg/concepts/overlay-ports#example-overlay-ports-example)

## Key Topics/Ideas

### Terms

- `port` is a versioned build recipe that produces a package
- `triplet` capures the target build environment in a single name
- `manifest` a listing of dependencies in the project that have optional features or version contstraints. This is the `vcpkg.json` file
- `registry` a catalog of ports and versions that a user can install. Could be public or local and contains customizations if needed
- `port file` describes to download, build, install, and package a specific C++ library from source using vcpkg. This is the `portfile.cmake` file

### Ideas & Concepts

- _Binary Caching_: Allows for the project to take in a binary rather than always build from source.
This could save a lot of time building the target code, but means that every library will need to be built at each release.
If a binary does not exist, the definition in the port file should describe how to build the code using vcpkg.

> Do we want to change how we do configration management for the common codebase?
> Or keep it so that when we release one thing we update versions of everything?

- _Asset Caching_: Allows for an "air gapped" install.
It basically copies what is in the target repo from an online source and copies it to a local registry.

- _Overlay Ports_: An overlay port can act as a drop-in replacement for an existing port or as a new port that is otherwise not available in a registry.
While resolving package names, overlay ports take priority.
This basically allows us to install things locally and cache locally.
It also allows us to have an environment that is seperate from others when in "Classic Mode".

- _Features_: A way to selectively add functionality, behavior, and dependencies from a library.
This could be extremely powerful for building our code and libraries especially with a mix of Clear, CUI, and High code.
We need to look into this.

## Setup

### Installation

```bash
# get the directories right
export VCPKG_DIR=/home/dave/playpen/vcpkg
export VCPKG_ROOT=$VCPKG_DIR/vcpkg

mkdir -p $VCPKG_DIR
cd $VCPKG_DIR

# get the repo and build it
git clone https://github.com/microsoft/vcpkg.git
cd vcpkg && ./bootstrap-vcpkg.sh -disableMetrics

# add it to path
export PATH=$VCPKG_ROOT:$PATH
```

### Manifest

A manifest has a listing of all of the libraries needed for building the code.
This is defaulted to be in a file called `vcpkg.json`.

Basic example:

```json
{
  "name": "vcpkg-sample-library",
  "version": "1.0.2",
  "homepage": "https://github.com/microsoft/vcpkg-docs/tree/cmake-sample-lib",
  "description": "A sample C++ library designed to serve as a foundational example for a tutorial on packaging libraries with vcpkg.",
  "license": "MIT",
  "dependencies": [
    {
      "name" : "vcpkg-cmake",
      "host" : true
    },
    {
      "name" : "vcpkg-cmake-config",
      "host" : true
    },
    "fmt"
  ]
}
```

- `name`: Specifies the name of the library. This is used as the package identifier.
- `version`: Indicates the version number of the library.
- `homepage`: URL to the project's homepage, often its repository. Useful for those who want to know more or contribute.
- `description`: Brief text describing what the library does. This is for documentation and users.
- `license`: Specifies the license under which the library is distributed.
- `dependencies`: An array containing the list of dependencies that the library needs.
- `name`: vcpkg-cmake: Specifies a dependency on vcpkg-cmake, which provides CMake functions and macros commonly used in vcpkg ports.
- `host`: true: Specifies that vcpkg-cmake is a host dependency, meaning it's required for building the package but not for using it.
- `name`: vcpkg-cmake-config: Specifies a dependency on vcpkg-cmake-config, which assists in using CMake config scripts.
- `fmt`: Specifies a run-time dependency on the fmt library. This means fmt is required for both - building and using the package.

#### Manifest Registry Config

You can redirect the registry to point elsewhere or to use specific tags/commits.
This way you can add more package registries or overlay port locations.

```json
{
  "default-registry": {
    "kind": "git",
    "baseline": "7476f0d4e77d3333fbb249657df8251c28c4faae",
    "repository": "https://github.com/microsoft/vcpkg"
  },
  "registries": [
    {
      "kind": "git",
      "repository": "https://github.com/northwindtraders/vcpkg-registry",
      "baseline": "dacf4de488094a384ca2c202b923ccc097956e0c",
      "packages": [ "beicode", "beison" ]
    }
  ],
  "overlay-ports": [
    "C:\\dev\\my_vcpkg_ports"
  ]
}
```

### Port File

A port file defines how to download, build, install, and package a specific C++ library.
This is basically CMake from what I can tell.

```cmake
vcpkg_check_linkage(ONLY_STATIC_LIBRARY)

vcpkg_from_github(
    OUT_SOURCE_PATH SOURCE_PATH
    REPO Microsoft/vcpkg-docs
    REF "${VERSION}"
    SHA512 0  # This is a temporary value. We will modify this value in the next section.
    HEAD_REF cmake-sample-lib
)


vcpkg_cmake_configure(
    SOURCE_PATH "${SOURCE_PATH}"
)

vcpkg_cmake_install()

vcpkg_cmake_config_fixup(PACKAGE_NAME "my_sample_lib")

file(REMOVE_RECURSE "${CURRENT_PACKAGES_DIR}/debug/include")

file(INSTALL "${SOURCE_PATH}/LICENSE" DESTINATION "${CURRENT_PACKAGES_DIR}/share/${PORT}" RENAME copyright)
configure_file("${CMAKE_CURRENT_LIST_DIR}/usage" "${CURRENT_PACKAGES_DIR}/share/${PORT}/usage" COPYONLY)
```

- `vcpkg_check_linkage(ONLY_STATIC_LIBRARY)`: Specifies that only static linking
  is supported for this package.
- `vcpkg_from_github`: Starts the function to download the source code from a
  GitHub repository.
  - `OUT_SOURCE_PATH SOURCE_PATH`: Sets the directory where the source code will
    be extracted.
  - `REPO JavierMatosD/vcpkg-sample-library`: The GitHub repository containing
    the source code.
  - `REF "${VERSION}"`: The version of the source code to download.
  - `SHA512 0`: Placeholder for the SHA-512 hash of the source code for
    integrity verification.
  - `HEAD_REF main`: Specifies the default branch for the repository.
- `vcpkg_cmake_configure`: Configures the project using CMake, setting up the build.
  - `SOURCE_PATH "${SOURCE_PATH}"`: The path to the source code downloaded earlier.
- `vcpkg_cmake_install()`: Builds and installs the package using CMake.
- `vcpkg_cmake_config_fixup(PACKAGE_NAME "my_sample_lib")`: Fixes the CMake
  package configuration files to be compatible with vcpkg.
- `file(REMOVE_RECURSE "${CURRENT_PACKAGES_DIR}/debug/include")`: Deletes the
  include directory from the debug installation to prevent overlap.
- `file(INSTALL "${SOURCE_PATH}/LICENSE" DESTINATION ...)`: Installs the LICENSE
  file to the package's share directory and renames it to copyright.
- `configure_file("${CMAKE_CURRENT_LIST_DIR}/usage" ...)`: Copies a usage
  instruction file to the package's share directory.

## Running

With the above all setup you can now use the vcpkg CLI

`vcpkg install vcpkg-sample-library`
