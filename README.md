# ACTS for FASER2
This repository contain the instruction to install and all the modification made to use ACTS for a FASER2 simulation

## ACTS installation
The github page and documentation can be found [here](https://github.com/acts-project/acts), good recent ACTS tutorial/installation [guide](https://github.com/andiwand/inner-detector-tracking-workshop-2023/tree/main/acts-examples-tutorial)
To install ACTS in an interactive server with access to cvmfs: 

Use this CVMFS before installing and each use of ACTS to have access to all depencies (otherwise quite tricky):
$ source /cvmfs/sw.hsf.org/spackages6/key4hep-stack/2023-01-15/x86_64-centos7-gcc11.2.0-opt/csapx/setup.sh

### Installation steps
```
$ git clone https://github.com/acts-project/acts <source>
$ cd source
$ git submodule init
$ git submodule update
$ cmake -B <build> -S <source>
$ cmake --build <build> \  -DCMAKE_BUILD_TYPE=RelWithDebInfo \
$  -DCMAKE_CXX_STANDARD=17 \
$  -DCMAKE_INSTALL_PREFIX="acts-install" \
$  -DACTS_BUILD_ODD=ON \
$  -DACTS_BUILD_FATRAS=ON \
$  -DACTS_BUILD_FATRAS_GEANT4=ON \
$  -DACTS_BUILD_EXAMPLES_DD4HEP=ON \
$  -DACTS_BUILD_EXAMPLES_GEANT4=ON \
$  -DACTS_BUILD_EXAMPLES_PYTHIA8=ON \
$  -DACTS_BUILD_EXAMPLES_PYTHON_BINDINGS=ON \
$  -DACTS_FORCE_ASSERTIONS=ON \
$  -DACTS_ENABLE_LOG_FAILURE_THRESHOLD=ON
```

ACTS needs to be source before each use:
```
$ source bin/this_acts.sh
$ source python/setup.sh
```

Setup can be testied using this tutorial chain example
$ Examples/Scripts/Python/full_chain_odd.py

