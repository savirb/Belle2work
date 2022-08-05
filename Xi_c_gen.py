# #gen script for Xi_c+                                                         

import basf2 as b2

# Define the path                                                               
mypath = b2.create_path()

# Load the EventInfoSetter module and set the exp/run/evt details               
mypath.add_module("EventInfoSetter", expList=1003, runList=0, evtNumList=20)

# Define the beam background (collision) files                                  
import glob as glob
# on kekcc '/group/belle2/BGFile/OfficialBKG/early_phase3/prerelease-03-01-00a/\
#overlay/phase31/BGx1/set0/*.root'                                               
# on linuxfarmb '/data/BelleII/data/BGOverlay/*.root'                           
bg = glob.glob('/data/BelleII/BGOverlay/*.root')

# Add the generator for Xi_c+ -> Sigma+ pi+ pi-                                    
from ROOT import Belle2
decfile = '/belle2work/sbasil/sigma/sigma.dec'

#generating continuum samples, requiring that every event has a certain particl\
                                                                               
import generators as ge
ge.add_inclusive_continuum_generator(path=mypath, finalstate='ccbar', particles=['Xi_c+'], userdecfile=decfile, include_conjugates=1)

# Add the simulation modules                                                    
import simulation as si
si.add_simulation(path=mypath)

# Add the trigger simulation modules                                            
#import L1trigger as tg
#tg.add_tsim(path=mypath, Belle2Phase="Phase3")

# Add the reconstruction modules                                                
import reconstruction as re
re.add_reconstruction(path=mypath)

# Write out the results in MDST format                                          
import mdst as mdst
mdst.add_mdst_output(path=mypath, mc=True, filename='sigma.mdst.root')

# Process all modules added to mypath                                           
b2.process(path=mypath)

# print out the summary                                                         
print(b2.statistics)


