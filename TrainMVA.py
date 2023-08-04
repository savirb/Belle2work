import basf2_mva

go = basf2_mva.GeneralOptions()
go.m_datafiles = basf2_mva.vector('train.root')
go.m_treename = 'xicp'
go.m_identifier = 'weightfile.root'
go.m_variables = basf2_mva.vector("p_protonID_noSVD",
                                  "K_kaonID_noSVD",
                                  "Lambdac_y",
                                  "Xic_alpha"
)
go.m_target_variable = 'Xic_isSignal'
go.m_method = "FastBDT"

sp = basf2_mva.FastBDTOptions()
#sp.m_nTrees = 600
#sp.m_shrinkage = 0.2
#sp.m_nCuts = 10
#sp.m_nLevels = 10
#sp.m_randRatio = 0.6
#sp.m_purityTransformation = 1
#sp = basf2_mva.TMVAOptionsClassification()
#sp.m_config = '!H:!V:CreateMVAPdfs:BoostType=Grad:NTrees=100:Shrinkage=0.2:MaxDepth=3'

basf2_mva.teacher(go, sp)

basf2_mva.expert(basf2_mva.vector('weightfile.root'),
                 basf2_mva.vector('train.root'), 'xicp', 'expert_train.root')

basf2_mva.expert(basf2_mva.vector('weightfile.root'),
                 basf2_mva.vector('test.root'), 'xicp', 'expert_test.root')
