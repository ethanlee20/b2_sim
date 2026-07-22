import sys

import basf2 as b2
import modularAnalysis as ma
from variables import collections as vc
from variables import utils as vu
from variables import variables as vm

# command line options

input_file_paths = sys.argv[1]  # overwritten on the Grid
output_file_path = sys.argv[2]  # choose something like recon.root

print("\n-- Reconstruction Configuration --")
print(f"Input file (overwritten on grid): {input_file_paths}")
print(f"Output file (modified on grid): {output_file_path}")
print("-----------------------------------\n")


# begin processing

main = b2.Path()


def append_global_tag():
    gt = ma.getAnalysisGlobaltag()
    b2.conditions.append_globaltag(gt)


def define_aliases():
    vm.addAlias("mcMother_mcPDG", "mcMother(mcPDG)")
    vm.addAlias("mcSister_0_mcPDG", "mcMother(mcDaughter(0, mcPDG))")
    vm.addAlias("mcSister_1_mcPDG", "mcMother(mcDaughter(1, mcPDG))")
    vm.addAlias("mcSister_2_mcPDG", "mcMother(mcDaughter(2, mcPDG))")
    vm.addAlias("mcSister_3_mcPDG", "mcMother(mcDaughter(3, mcPDG))")
    vm.addAlias("mcSister_4_mcPDG", "mcMother(mcDaughter(4, mcPDG))")
    vm.addAlias("mcSister_5_mcPDG", "mcMother(mcDaughter(5, mcPDG))")
    vm.addAlias("mcSister_6_mcPDG", "mcMother(mcDaughter(6, mcPDG))")
    vm.addAlias("mcSister_7_mcPDG", "mcMother(mcDaughter(7, mcPDG))")
    vm.addAlias("mcSister_8_mcPDG", "mcMother(mcDaughter(8, mcPDG))")
    vm.addAlias("mcSister_9_mcPDG", "mcMother(mcDaughter(9, mcPDG))")


def input_to_the_path():
    ma.inputMdstList(
        filelist=input_file_paths,
        path=main,
        environmentType="default",
    )


def reconstruct_generator_level():
    ma.fillParticleListFromMC(decayString="K+:gen", cut="", path=main)
    ma.fillParticleListFromMC(decayString="pi-:gen", cut="", path=main)
    ma.fillParticleListFromMC(decayString="mu+:gen", cut="", path=main)

    ma.reconstructMCDecay("K*0:gen =direct=> K+:gen pi-:gen", cut="", path=main)
    ma.reconstructMCDecay("B0:gen =direct=> K*0:gen mu+:gen mu-:gen", cut="", path=main)


def create_variable_lists():
    std_vars = (
        vc.deltae_mbc
        + vc.inv_mass
        + vc.mc_truth
        + ["mcMother_mcPDG"]
        + ["PDG"]
        + [
            "mcSister_0_mcPDG",
            "mcSister_1_mcPDG",
            "mcSister_2_mcPDG",
            "mcSister_3_mcPDG",
            "mcSister_4_mcPDG",
            "mcSister_5_mcPDG",
            "mcSister_6_mcPDG",
            "mcSister_7_mcPDG",
            "mcSister_8_mcPDG",
            "mcSister_9_mcPDG",
        ]
        + vc.pid
        + vc.kinematics
        + vc.mc_kinematics
        + ["dr", "dz"]
        + ["theta", "thetaErr", "mcTheta"]
        + ["isSignalAcceptBremsPhotons"]
    )

    Kstar0_vars = vu.create_aliases_for_selected(
        list_of_variables=std_vars,
        decay_string="B0 -> [^K*0 -> K+ pi-] mu+ mu-",
    )

    K_pi_vars = vu.create_aliases_for_selected(
        list_of_variables=std_vars,
        decay_string="B0 -> [K*0 -> ^K+ ^pi-] mu+ mu-",
        prefix=["K_p", "pi_m"],
    )

    lepton_vars = vu.create_aliases_for_selected(
        list_of_variables=std_vars,
        decay_string="B0 -> [K*0 -> K+ pi-] ^mu+ ^mu-",
        prefix=["mu_p", "mu_m"],
    )

    out = std_vars + Kstar0_vars + K_pi_vars + lepton_vars
    return out


def save_output(B0_vars, sim_level, file_path):
    ma.variablesToNtuple(
        decayString=f"B0:{sim_level}",
        variables=B0_vars,
        filename=file_path,
        treename=sim_level,
        path=main,
    )


append_global_tag()
define_aliases()
input_to_the_path()
reconstruct_generator_level()
B0_vars = create_variable_lists()
save_output(B0_vars, "gen", output_file_path)
b2.process(main)
print(b2.statistics)
