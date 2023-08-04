import numpy as np
import pandas as pd
import root_pandas
from matplotlib import gridspec
import matplotlib.pyplot as plt
%matplotlib inline

import ROOT as r
r.gROOT.LoadMacro('/belle2work/BelleII/belle2style/Belle2Style.C') 
r.SetBelle2Style()

# Make nice looking plots
plt.rcParams.update({
          'font.size': 20,
          'figure.figsize': (12, 8),
})

signalfile ='/belle2work/sbasil/lambdacpi0/fromBelleII/xic_signal.root'
ccfile = '/belle2work/BelleII/XicToLcpi0/MC15rd/ccbar_temp.root'

mycols = ["Xic_DeltaM","Lambdac_M"]
mccols = ["Xic_isSignal","Lambdac_isSignal","Lambdac_genMotherPDG","pi0_genMotherPDG","pi0_mcPDG","Lambdac_mcPDG"]

input_vars = open("/belle2work/sbasil/lambdacpi0/fromBelleII/vars.txt").read().strip().split()
for i in input_vars:
    mycols.append(i)

mycuts = 'Lambdac_M>2.25 & Lambdac_M<2.32 & Xic_DeltaM > 0.12 & Xic_DeltaM < 0.325'

df_sig = root_pandas.read_root(signalfile, key='xicp', columns=mycols+mccols, where=mycuts)
df_cc = root_pandas.read_root(ccfile, key='xicp', columns=mycols+mccols, where=mycuts)

charmbgs = '((abs(Lambdac_mcPDG)==411 and abs(Lambdac_genMotherPDG)==413) or (abs(Lambdac_mcPDG)==421 and abs(Lambdac_genMotherPDG)==423) or (abs(Lambdac_mcPDG)==431 and abs(Lambdac_genMotherPDG)==433))'
sigmast = '(pi0_mcPDG==111 and Lambdac_isSignal==1 and ((abs(Lambdac_genMotherPDG)==4212 and abs(pi0_genMotherPDG)==4212)))'
sigmastst = '(pi0_mcPDG==111 and Lambdac_isSignal==1 and ((abs(Lambdac_genMotherPDG)==4214 and abs(pi0_genMotherPDG)==4214)))'

cuts = mycuts

base_df = df_sig.query(cuts+' and Xic_isSignal==1')

#qq -> base_qq
base_qq = df_cc.query(cuts+' and not Xic_isSignal==1 and not Lambdac_isSignal==1 and not '+charmbgs+' and not '+sigmast+' and not '+sigmastst)
#other 5 bkgs
base_dst = df_cc.query(cuts+' and not Xic_isSignal==1 and '+charmbgs)
base_sigmastst = df_cc.query(cuts+' and not Xic_isSignal==1 and '+sigmastst)
base_sigmast = df_cc.query(cuts+' and not Xic_isSignal==1 and '+sigmast)
base_mis = df_sig.query(cuts+' and not Xic_isSignal==1')
base_Lc = df_cc.query(cuts+' and not Xic_isSignal==1 and Lambdac_isSignal==1 and not '+charmbgs+' and not '+sigmast+' and not '+sigmastst)

#form one base_bkg
frames = [base_qq, base_dst, base_sigmastst, base_Lc, base_mis, base_sigmast]
base_bkg = pd.concat(frames)

def optimalCutFinal(var):
    nptrue = base_df[var].to_numpy()
    npbkg = base_bkg[var].to_numpy()

    maxtrue = max(nptrue)
    mintrue = min(nptrue)

    myrange=(mintrue,maxtrue)

    signal_without_cuts = len(nptrue)
    bkg_without_cuts = len(npbkg)

    testvalue = mintrue
    mytestvalue=0
    mytotal=0

    for i in range(100):    
        nptrue = nptrue[nptrue > testvalue]
        npbkg = npbkg[npbkg > testvalue]

        signal_efficiency = (len(nptrue))/signal_without_cuts
        background_rejection = 1-(len(npbkg)/bkg_without_cuts)
        total=signal_efficiency+background_rejection

        if total > mytotal:
            mytotal = total
            mytestvalue = testvalue

        testvalue+=((maxtrue-mintrue)/100)

    print(mytotal,var + " > " + str(mytestvalue))
    
def optimalCutLessFinal(var):
    
    nptrue = base_df[var].to_numpy()
    npbkg = base_bkg[var].to_numpy()

    maxtrue = max(nptrue)
    mintrue = min(nptrue)

    myrange=(mintrue,maxtrue)

    signal_without_cuts = len(nptrue)
    bkg_without_cuts = len(npbkg)

    testvalue = maxtrue
    mytestvalue=0
    mytotal=0

    for i in range(100):    
        nptrue = nptrue[nptrue < testvalue]
        npbkg = npbkg[npbkg < testvalue]

        signal_efficiency = (len(nptrue))/signal_without_cuts
        background_rejection = 1-(len(npbkg)/bkg_without_cuts)
        total=signal_efficiency+background_rejection

        if total > mytotal:
            mytotal = total
            mytestvalue = testvalue

        testvalue-=((maxtrue-mintrue)/100)

    print(mytotal,var + " < " + str(mytestvalue))

for test in mycols[2:]:
    try:
        optimalCutFinal(test)
    except:
        print(test+": NaN")
    try:
        optimalCutLessFinal(test)
    except:
        print(test+": NaN")
