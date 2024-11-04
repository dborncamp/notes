# Hypatia

## Background

[The paper presenting Hypatia](https://dl.acm.org/doi/abs/10.1145/3419394.3423635) (with videos).
Author notes and documentation for the underlying simulator framework can be found in the [docs folder of the `basic-sim` repo](https://github.com/snkas/basic-sim/tree/master/doc)

Hypatia is mostly a Python library so lets start by making a virtual environment for it.
A working Python environment is needed which means following [ITS's artifactory instructions](https://confluence.aero.ball.com/display/ASC/Artifactory+Repo+Guide+for+Developers#ArtifactoryRepoGuideforDevelopers-pypi) (since they block PyPi on normal Aero machines) see below for instructions.
The existing shell scripts expect a debian based environment, not the given RHEL environment so if using the installation scripts provided in the repo, that will need to change.

Hypatia is a mix of C++ and Python with Cython reading in a lot of the C++ into Python.
This makes for an interesting system that can be hard to extend.

## Open Questions

- Will we be expecting a "bursty" network?
- Will we be using TLS?
- How will tunneling be handled and do we care about it?

## Terminology/Acronyms in This Repo

- `ISL` - Inter-Satelite Link - Defines the network of satellites
- `GS` - Ground Station
- `TLE` - Two Line Element - A common data format from [NROAD to define satellite ephemris for satellites](https://celestrak.org/NORAD/documentation/tle-fmt.php)

## Installation

**NOTE**: Also see the Dockerfile for full build instructions.
It is built on a fat image so it should have many debugging tools for Python and networking included.
This can be slimmed down by using a multi-stage build process and using an Alpine or even a distroless base image for use in production.

This cannot be built as is using Python 3.12+ because it relies on `imp` which is no longer part of the standard library.

### SMS Specific Setup

Create the pip configuration in `~/.pip/pip.conf`:

```toml
[global]
index-url = https://arti.bsf.ball.com/artifactory/api/pypi/pypi_group/simple
trusted-hosts = arti.bsf.ball.com
extra-index-url = https://arti.bsf.ball.com/artifactory/api/pypi/pypi_group/simple/
#Location should be to Ball.pem
export PIP_CERT=/usr/local/share/ca-certificates/AEROISSUECA02-CA.crt
```

Where `/usr/local/share/ca-certificates/AEROISSUECA02-CA.crt` is [this certificate, AEROISSUECA02-CA](https://pki.aero.ball.com/pki/AEROISSUECA02-CA(1).crt)

### Create Python Virtual Env

A Python virtual environment is a great idea so that it does't mess up your bigger environment

```bash
python3 -m venv hypatia_env
source hypatia_env/bin/activate
pip install --upgrade pip setuptools
```

### Hypatia Install Scripts

You will need to update line 14 of the `hypatia_install_dependencies.sh` script to use `-y` on the install otherwise it will not install everything since it pipes the output to true.

```bash
sh hypatia_install_dependencies.sh
sh hypatia_build.sh
```

### Run Hypatia's Tests

There are a series of unit tests and other tests that basically go through what was needed to make the figures and analysis in the paper.
Snkas made this really easy to run by giving a shell script `hypatia_run_tests.sh` to do this.
While not particularly useful for us, it is good to ensure that it was installed correctly.
It will take several minutes to run to completion and will create many .pdfs that can be viewed (eg `find . -name *.pdf` and ignore the things in `hypatia_env`).

## Simulation

### Intended Use

The library is not make as an SDK, it is really intended to be given a series of input files that represent both the orbits of satellites and the intended communications between locations on the ground at a given time.
More information and examples on how to use it can be found in [the paper expexperiments](https://github.com/snkas/hypatia/blob/master/paper/ns3_experiments/README.md) documentation.

It is also intended to be used with [Cesium](https://ion.cesium.com/) for graphicall viewing over the planet.

### Breaking It To Suit Our Needs

Most of what we care about will be in the `satgen` module.
This is what defined the algorithms that are used to simulate communications between satellite network.
We will likely want to take the `algorithm_paired_many_over_isls` algorithm and update it for our needs since it starts up pretty close to what we want.
The function will return a dictionary which contains:

- The duration it took
- Number of satellites that it used
- How many ground stations (we will need to alter the alg to fit our needs)
- The paired satellites that were used or the bandwidth of those satellites

The [basic-sim repo](https://github.com/snkas/basic-sim) (which Hypatia uses) is also used here to simulate the network, this can also be used to help simulate what we need.
It supports latency modeling, UDP bursting, and TCP flows as well as plotting and visualizing what is happening.
It is [fairly well documented](https://github.com/snkas/basic-sim/blob/master/doc/) and has some helpful notes about what is happening and how to get started with a simulation.

## Future Recommendations

### Data Needs

The satellites that are defined here are years out of date.
We should get updated satellite swarm [information from the FAA](https://www.nstb.tc.faa.gov/RTData_WaasSatelliteData.htm) to better simulate a modern network.
[NORAD CelesTrak](https://celestrak.org/NORAD/elements/supplemental/) also has TLE data that is specific for StarLink through at least late 2024.

For tracking satellites and scheduling passes, we may want to use [some of the public software from CelesTrak](https://celestrak.org/software/tskelso-sw.php) and [a larger library](https://celestrak.org/software/satellite/sat-trak.php).

### Simulations

The Hypatia repo itself is not designed to be extended in the way that we would need it to be, but we can take the algorithms and how it handles the data.
See [Breaking It To Suit Our Needs](#breaking-it-to-suit-our-needs) for more information.
We should also take the ability to read in the data formats which is in the Hypatia repo itself as that can be extended to suit our needs.
