import os
import yaml
from rdkit import Chem
from rdkit.Chem import AllChem


def load_config(config_file="config.yaml"):
    with open(config_file, "r") as f:
        return yaml.safe_load(f)


def generate_gaussian_input(cfg):
    mol = Chem.MolFromSmiles(cfg["smiles"])
    mol = Chem.AddHs(mol)
    AllChem.EmbedMolecule(mol)
    AllChem.UFFOptimizeMolecule(mol)
    conf = mol.GetConformer()

    com_file = f"{cfg['job_name']}.com"
    with open(com_file, "w") as f:
        f.write(f"%nprocshared={cfg['cores']}\n")
        f.write(f"%mem={cfg['cores'] * cfg['mem_per_cpu']}MB\n")
        f.write(f"# opt {cfg['functional']}/{cfg['basis_set']}\n\n")
        f.write(f"{cfg['job_name']} optimization\n\n")
        f.write(f"{cfg['charge']} {cfg['multiplicity']}\n")
        for atom in mol.GetAtoms():
            pos = conf.GetAtomPosition(atom.GetIdx())
            f.write(f"{atom.GetSymbol()} {pos.x:.6f} {pos.y:.6f} {pos.z:.6f}\n")
        f.write("\n")
    return com_file


def generate_slurm_script(cfg, com_file):
    workdir = f"/work_bgfs/{cfg['user'][0]}/{cfg['user']}"
    email = f"{cfg['user']}@{cfg['email_domain']}"

    sl_file = f"{cfg['job_name']}.sl"
    slurm_template = f"""#!/bin/bash
#SBATCH --job-name={cfg['job_name']}
#SBATCH --mail-type=ALL
#SBATCH --mail-user={email}
#SBATCH -t {cfg['time']}
#SBATCH -n {cfg['cores']}
#SBATCH -p {cfg['partition']}
#SBATCH -q {cfg['queue']}
#SBATCH --mem-per-cpu {cfg['mem_per_cpu']}

module add apps/gaussian/09b01_amd64
which g09
input={com_file}
output=$input.out
echo 'SLURM_JOB_NAME': $SLURM_JOB_NAME
echo 'SLURM_JOB_ID': $SLURM_JOB_ID

WorkDir={workdir}/$SLURM_JOB_NAME
SubmitDir=`pwd`

GAUSS_SCRDIR={workdir}/g09/$SLURM_JOB_NAME-$SLURM_JOB_ID
export GAUSS_SCRDIR

mkdir -p $GAUSS_SCRDIR
mkdir -p $WorkDir

cd $WorkDir
cp $SubmitDir/$input .

g09 < $input > $output
cp * $SubmitDir/

rm -rf $GAUSS_SCRDIR
rm -rf $WorkDir
"""
    with open(sl_file, "w") as f:
        f.write(slurm_template)
    return sl_file


def main():
    cfg = load_config()
    com_file = generate_gaussian_input(cfg)
    sl_file = generate_slurm_script(cfg, com_file)
    print(f"Generated {com_file} and {sl_file}")


if __name__ == "__main__":
    main()
