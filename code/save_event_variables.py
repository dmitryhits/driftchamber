"""
This script reads all the rootfiles which were converted datfiles and extracts
meaningful event variables which can be used in the analysis. Those variables
will be saved in a tree for each run und all trees will be saved to one single
rootfile for convenience. The idea is that all other analysis scrips only read
this new rootfile. If some information is missing, this script should be editetd
to save an imporved set of event variables.
"""

from ROOT import TFile, TGraph, TF1, TTree, TTimeStamp, AddressOf
from sys import argv
from numpy import array, argmax, mean, float32, zeros, uint32, diff, argmin
from scipy.integrate import simps
import os

# Method for rebinning. 2^n bins will be combined.
def rebin(array, n):
    for i in range(n):
        if i == 0:
            rebin = (array[:-1:2] + array[1::2])/2
        else:
            rebin = (rebin[:-1:2] + rebin[1::2])/2
    return rebin

# Number of voltage measurements in each channel per event
n = 1024

# Location of the initial rootfiles and filename of the new one
rootfiles_dir = "../rootfiles/"
outfile = TFile("../data.root", 'recreate')

# Getting the driftchanber channel corresponding to a DRS channel
c = [1, 3, 7, 8]

# Variables for the input tree
t = [zeros(n, dtype=float32) for i in range(4)]
v = [zeros(n, dtype=float32) for i in range(4)]
eventn_in = zeros(1, dtype=uint32)
timestamp = TTimeStamp()

# Variables for the output tree
eventn = zeros(1, dtype=uint32)
seconds = zeros(1, dtype=uint32) # seconds passed until the beginning
height = [zeros(1, dtype=float32) for i in range(4)]
time = [zeros(1, dtype=float32) for i in range(4)]
chi2 = [zeros(1, dtype=float32) for i in range(4)]
integral = [zeros(1, dtype=float32) for i in range(4)]

# Save event variables for the run stored in 'filename' in a tree called
# 'treename' and save this tree to 'outfile'
def save_event_tree(filename, treename):

    # Read in rootfile and tree
    f = TFile(filename)
    intree = f.Get('tree')
    intree.SetBranchAddress("EventNumber", eventn_in)

    # Create a tree to save the event variables in
    outtree = TTree(treename, treename)

    # Get the number of events
    N = intree.GetEntries()

    # Find out what the number of channels in this run was
    n_ch = 0
    for i in range(1, 5):
        branch = intree.GetBranch("chn{}_t".format(i))
        if branch == None:
            break
        else:
            n_ch = n_ch + 1

    # Initiate branches accorting to the number of channels
    for i in range(n_ch):
        intree.SetBranchAddress("chn{}_t".format(i+1), t[i])
        intree.SetBranchAddress("chn{}_v".format(i+1), v[i])
        intree.SetBranchAddress("EventDateTime", AddressOf(timestamp))

        # Just comment out the branches which are not needed in the final tree
        #outtree.Branch("EventN", eventn, "EventN/i")
        #outtree.Branch("Seconds", seconds, "Seconds/i")
        outtree.Branch("Chn{}_Height".format(c[i]), height[i], "Chn{}_Height/F".format(c[i]))
        outtree.Branch("Chn{}_Time".format(c[i]), time[i], "Chn{}_Time/F".format(c[i]))
        #outtree.Branch("Chn{}_Chi2".format(c[i]), chi2[i], "Chn{}_Chi2/F".format(c[i]))
        #outtree.Branch("Chn{}_Integral".format(c[i]), integral[i], "Chn{}_Integral/F".format(c[i]))


    starting_seconds = 0
    # This loop iterates over each event
    for j in range(N):
        intree.GetEntry(j)
        eventn[0] = eventn_in[0]
        if j == 0:
            starting_seconds = timestamp.GetSec()
        seconds[0] = timestamp.GetSec() - starting_seconds

        # This loop iterates over each channel
        for i in range(n_ch):

            # Rebin
            t_re = rebin(t[i], 3)
            v_re = rebin(v[i], 3)

            # Calculate noise baseline by averaging the signal in a range
            # before triggering happened
            noise_lvl = mean(v[:30])

            # Create a graph and fit it with Landau, as its chi2 will be one
            # event variable to distingush good from bad events
            gr = TGraph(int(n/8.), array(t_re, dtype=float),
                    -array(v_re, dtype=float)+noise_lvl)
            gr.Fit("landau", "Q")
            fit = gr.GetFunction("landau")
            chi2[i][0] = fit.GetChisquare()
            # As the time of the signal we define the minimum of the derivative
            d = diff(v_re)/diff(t_re)
            vd = (v_re[:-1] + v_re[1:])/2
            td = (t_re[:-1] + t_re[1:])/2
            time[i][0] = td[argmin(d)]
            # The height is defined as the maximum in the 10 bins following the
            # signals time position
            height[i][0] = max(-v_re[argmin(d):min(argmin(d) + 10,128)] - noise_lvl)

            # Get the highest value (alternative measure for heigh)
            # and the pulse integral
            #height[i][0] = -min(v_re - noise_lvl)
            integral[i][0] = -simps(v_re-noise_lvl, x=t_re)

        outtree.Fill()

    # Write tree and clean up
    outfile.cd()
    outtree.Write()
    f.Close()

# Process all rootfiles in the rootfiles directory (including subdirectories)
for path, subdirs, files in os.walk(rootfiles_dir):
    for name in files:
        if name.endswith(".root"):
            filename = os.path.join(path, name)
            treename =  filename[len(rootfiles_dir):-5].replace("/", "_")
            print("Processing {}...".format(filename))
            save_event_tree(filename, treename)

# Clean up
outfile.Close()
