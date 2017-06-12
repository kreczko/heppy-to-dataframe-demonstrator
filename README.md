# ra1-demonstrator
Demonstrate the use of AlphaTwirl in RA1 analyses

I'm building up to a full demonstration of analysis by working out each additional step as 
a separate sub-directory of this package.

The steps I want to take to get to a full demonstration are:
1. Local file - Make a dataframe with similar binning to RA1
2. Local file - Apply an event selection, build dataframe, similar to RA1
2. Local file - Add a scribbler, apply an event selection, build dataframe, similar to RA1
3. Remote file - Apply an event selection, build dataframe, similar to RA1
4. Remote file - Read in multiple files in parallel
5. What do the dataframes need to look like to reproduce the StatsAnalyzer optimizeBinning script outputs?
6. Reproduce statsAnalyzer input

# Dependence on the alphatwirl-interface repo
This package builds off the alphatwirl-interface repo which is still in development and therefore fairly experimental.
Work here is likely to influence work there and vice versa, so things may change often and significantly

# Usage
## Download and setup
It should be sufficient to checkout this package (and it's submodules), source the setup script and start testing each step's run script.
These steps can be achieved by doing:
```
git clone --recursive git@github.com:benkrikler/ra1-demonstrator.git
cd ra1-demonstrator
source setup.sh
```
__Please note__ that I have only tested this on Soolin so far, since that is where the eventual RA1 trees are located.
In the final version of this package, it should work on any grid-connected system.

## Running
It should be sufficient to change into the directory for the step you want to run, and execute the run script.
For step2, for example, you can do:
```
$ cd step2_local_eventSelection/
$ ./run.py ../data/20170129_Summer16_newJECs--ZJetsToNuNu_HT100to200_madgraph--treeProducerSusyAlphaT--tree.root
```

Each run script can show you the options it accepts by doing:
```
./run.py --help
```
