import streamlit as st
import yaml
from Pipe import generate_gaussian_input, generate_slurm_script

# Load defaults
with open("config.yaml") as f:
    cfg = yaml.safe_load(f)

st.title("SLURM + Gaussian Job Generator")

cfg["job_name"] = st.text_input("Job Name", cfg.get("job_name", "ethylacrylate"))
cfg["smiles"] = st.text_input("SMILES", cfg.get("smiles", "CCOC(=O)C=C"))
cfg["user"] = st.text_input("Username", cfg.get("user", "dlockridge"))
cfg["email_domain"] = st.text_input("Email domain", cfg.get("email_domain", "usf.edu"))
cfg["time"] = st.text_input("Time", cfg.get("time", "21-00:00:00"))
cfg["cores"] = st.number_input("Cores", value=cfg.get("cores", 20), min_value=1)
cfg["partition"] = st.selectbox("Partition", ["chbme_2018", "general", "himem"], index=0)
cfg["queue"] = st.selectbox("Queue", ["chbme18", "general"], index=0)
cfg["mem_per_cpu"] = st.number_input("Memory per CPU (MB)", value=cfg.get("mem_per_cpu", 5000))

if st.button("Generate Job Files"):
    com_file = generate_gaussian_input(cfg)
    sl_file = generate_slurm_script(cfg, com_file)
    st.success(f"Generated {com_file} and {sl_file}")
    st.download_button("Download SLURM Script", open(sl_file, "rb").read(), file_name=sl_file)
    st.download_button("Download Gaussian Input", open(com_file, "rb").read(), file_name=com_file)
