import basf2 as b2
import modularAnalysis as ma
import variables as va
import stdPhotons as st
import vertex as vx
import variables.collections as vc
import variables.utils as vu

mypath = b2.create_path()

infile = '/belle2work/sbasil/condor/rootfiles/signal_before_rec.root'

output_file = 'recsigmasignalfinal.root'

# Load input file
ma.inputMdstList(environmentType='default', filelist=infile, path=mypath)

# track cuts
goodTrack1 = 'thetaInCDCAcceptance'
goodTrack2 = 'nCDCHits > 20'
ipcut = 'abs(dz) < 2.0 and abs(dr)<0.5 and nPXDHits>0 and nSVDHits>0'
protoncut = 'protonID>0.2'

#only need pi+ list, itll get the minus list too
ma.fillParticleList('pi+:mypi', cut=goodTrack1+' and '+goodTrack2+' and '+ipcut, path=mypath)
ma.fillParticleList('p+:myp', cut=goodTrack1+' and '+goodTrack2+' and '+protoncut, path=mypath)

#loose cuts
Xi_c_cuts = '2.3 < M < 2.7 and  useCMSFrame(p) > 2.5'
Sigma_cuts = '1.0 < M < 1.3'

#pi0
st.stdPhotons(listtype = 'all', path=mypath)
ma.cutAndCopyList('gamma:eff40_Jan2020','gamma:all','[ [clusterReg==1 and E>0.080] or [clusterReg==2 and E>0.030] or [clusterReg==3 and E>0.060] ] ', path=mypath)
ma.reconstructDecay(decayString = 'pi0:mypi0 -> gamma:eff40_Jan2020 gamma:eff40_Jan2020', cut = '0.120<M<0.145', path=mypath)

#reconstruct Sigma+
ma.reconstructDecay('Sigma+:ppi0 -> p+:myp pi0:mypi0', cut=Sigma_cuts, dmID=1, path=mypath)

#reconstruct Xi_c+
ma.reconstructDecay('Xi_c+:Sigma+pipi -> Sigma+:ppi0 pi+:mypi pi-:mypi', cut=Xi_c_cuts, dmID=1, path=mypath)

# Apply a vertex fit for the Xi_c+
vx.treeFit('Xi_c+:Sigma+pipi', conf_level=0.001, updateAllDaughters=True, ipConstraint=True, path=mypath)

# Define aliases for the vertex results
va.variables.addAlias('vtxChi2','extraInfo(chiSquared)')
va.variables.addAlias('vtxNDF','extraInfo(ndf)')
va.variables.addAlias('Xic_px_CMS','useCMSFrame(px)')
va.variables.addAlias('Xic_py_CMS','useCMSFrame(py)')
va.variables.addAlias('Xic_pz_CMS','useCMSFrame(pz)')
va.variables.addAlias('Xic_p_CMS','useCMSFrame(p)')
cms_variables = ['Xic_px_CMS','Xic_py_CMS','Xic_pz_CMS','Xic_p_CMS']

# Do MC matching for the Xi_c+
ma.matchMCTruth("Xi_c+:Sigma+pipi", path = mypath)

# Define the variables we want to include for all particles
common_vars = vu.create_aliases_for_selected(
    list_of_variables = vc.mc_truth + vc.kinematics, 
    decay_string='^Xi_c+ -> [^Sigma+ -> ^p+ [^pi0 -> ^gamma ^gamma]] ^pi+  ^pi-',
    prefix=['xic','sigma','sigma_p','sigma_pi0','gamma1','gamma2','xic_pi1','xic_pi2'])
# Define the variables we want to include for charged final state
charged_vars = vu.create_aliases_for_selected(
    list_of_variables = vc.pid + vc.inv_mass + vc.track + vc.track_hits, 
    decay_string='^Xi_c+ -> [^Sigma+ -> ^p+ [pi0 -> gamma gamma]] ^pi+ ^pi-',
    prefix=['xic','sigma','sigma_p', 'xic_pi1','xic_pi2'])

vertex_vars = vu.create_aliases_for_selected(
    list_of_variables=['dM', 'vtxChi2', 'vtxNDF'] + vc.inv_mass + vc.flight_info + vc.vertex + vc.mc_flight_info + vc.mc_vertex,
    decay_string='^Xi_c+ -> [^Sigma+ -> p+ [pi0 -> gamma gamma]] pi+ pi-',
    prefix=['xic','sigma'])

#define variables for neutral particles
neutral_vars = vu.create_aliases_for_selected(
    list_of_variables=vc.cluster,
    decay_string='Xi_c+ -> [Sigma+ -> p+ [^pi0 -> ^gamma ^gamma]] pi+ pi-',
    prefix=['sigma_pi0','gamma1','gamma2'])

# Write variables to an ntuple file
ma.variablesToNtuple('Xi_c+:Sigma+pipi', common_vars + charged_vars + vertex_vars + neutral_vars,
                     filename=output_file, treename= 'xic_tree', path=mypath)

# Process the path
b2.process(path=mypath)
print(b2.statistics)
