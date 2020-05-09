# Measuring cosmic muons with a driftchamber
## Overview
The driftchamber experiments in advanced practical physics class. The data with
the driftchamber events can be found in \[1\].

## Scripts
### decode.py and rootfiles.sh
The python script *decode.py* can be used to convert binary data files from the
DRS evaluation board \[2\] to ROOT files and is based on an older script which
doesn't work with the newest version of the binary data format anymore \[3\].
The bash script *rootfiles.sh* converts the complete data set to rootfiles
using the python script on the individual data files. It requires the data
archive \[1\] to be in the same directory.

### pmt.py
Plots the measured count rate vs high voltage (HV) for both photomultipliers in
the trigger system. The measurement data is included in the script.

### save\_event\_variables.py
Reads all files generated by *rootfiles.sh* and calculates meaningful event
variables from the raw voltage measurement. They get all saved in a single
rootfile, with one tree for each run.

### gasamp.py
A plot with the gas amplification measurements for different preassures and
anode voltages is generated.

### drift.py
This script plots drift velocity against field voltage.

### mc.py
With this script, one can do a monte carlo simulation to see how the
muon tracks are distributed in the wire chamber and compare with measurement.

### tracks.py
Generates plots showing the distribution on incident angles and positions.

## References
\[2\]: https://polybox.ethz.ch/index.php/s/6WYbMPdgEID5oBW

\[2\]: https://www.psi.ch/drs/evaluation-board

\[3\]: https://github.com/gkasieczka/testbeam/blob/master/decode.py

Short update

