import subprocess

components = [
    # {"flags": "Accuracy", "exp_per_slurm_job": "20", "trials_per_exp": "100"},
    # {"flags": "Entropy", "exp_per_slurm_job": "20", "trials_per_exp": "100"},
    # {"flags": "Diversity", "exp_per_slurm_job": "20", "trials_per_exp": "100"},
    {"flags": "DEV", "exp_per_slurm_job": "20", "trials_per_exp": "100"},
    {"flags": "DEVBinary", "exp_per_slurm_job": "20", "trials_per_exp": "100"},
    # {"flags": "SND", "exp_per_slurm_job": "15", "trials_per_exp": "100"},
    {"flags": "DomainCluster", "exp_per_slurm_job": "20", "trials_per_exp": "100"},
    {
        "flags": "ClassAMICentroidInit",
        "exp_per_slurm_job": "20",
        "trials_per_exp": "100",
    },
    {"flags": "MMD", "exp_per_slurm_job": "20", "trials_per_exp": "100"},
    {"flags": "BNM", "exp_per_slurm_job": "20", "trials_per_exp": "100"},
]

exp_names = ["atdoc", "bnm", "bsp", "cdan", "dann", "gvb", "im", "mcc", "mcd", "mmd"]
exp_names = " ".join(exp_names)

for x in components:
    command = "python validator_tests/run_validators.py --exp_group_prefix officehome --exp_group_contains fl6 --slurm_config a100 --run"
    command += f" --exp_names {exp_names} --flags {x['flags']} --exp_per_slurm_job {x['exp_per_slurm_job']} --trials_per_exp {x['trials_per_exp']}"
    subprocess.run(command.split(" "))
