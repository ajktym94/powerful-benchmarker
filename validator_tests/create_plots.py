import argparse
import os
import sys

import pandas as pd

sys.path.insert(0, ".")
from powerful_benchmarker.utils.constants import add_default_args
from validator_tests.utils.constants import (
    ALL_DFS_FILENAME,
    PER_SRC_FILENAME,
    PER_TARGET_FILENAME,
)
from validator_tests.utils.corr_utils import (
    get_corr_per_task,
    get_corr_per_task_per_adapter,
    get_per_threshold,
)
from validator_tests.utils.df_utils import (
    assert_acc_rows_are_correct,
    convert_list_to_tuple,
    exp_specific_columns,
    get_all_acc,
)
from validator_tests.utils.plot_corr_vs_src import plot_corr_vs_X
from validator_tests.utils.plot_val_vs_acc import plot_val_vs_acc


def read_all_dfs(exp_folder):
    df_path = os.path.join(exp_folder, ALL_DFS_FILENAME)
    return pd.read_pickle(df_path)


def process_acc_validator(df):
    convert_list_to_tuple(df)
    accs = get_all_acc(df)
    df = df.merge(accs, on=exp_specific_columns(df))
    assert_acc_rows_are_correct(df)
    return df


def get_per_src_per_target(df, exp_folder):
    src_filename = os.path.join(exp_folder, PER_SRC_FILENAME)
    target_filename = os.path.join(exp_folder, PER_TARGET_FILENAME)
    if (not os.path.isfile(src_filename)) or (not os.path.isfile(target_filename)):
        per_src, per_target = get_per_threshold(df, get_corr_per_task())
        per_src.to_pickle(os.path.join(exp_folder, PER_SRC_FILENAME))
        per_target.to_pickle(os.path.join(exp_folder, PER_TARGET_FILENAME))
    else:
        per_src = pd.read_pickle(src_filename)
        per_target = pd.read_pickle(target_filename)
    return per_src, per_target


def main(args):
    exp_folder = os.path.join(args.exp_folder, args.exp_group)
    df = read_all_dfs(exp_folder)
    df = process_acc_validator(df)
    plot_val_vs_acc(df, args.plots_folder)

    per_src, per_target = get_per_src_per_target(df, exp_folder)
    plot_corr_vs_X("src", False)(per_src, args.plots_folder)
    plot_corr_vs_X("target", False)(per_target, args.plots_folder)

    per_src, per_target = get_per_threshold(df, get_corr_per_task_per_adapter())
    plot_corr_vs_X("src", True)(per_src, args.plots_folder)
    plot_corr_vs_X("target", True)(per_target, args.plots_folder)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(allow_abbrev=False)
    add_default_args(parser, ["exp_folder"])
    parser.add_argument("--exp_group", type=str, required=True)
    parser.add_argument("--plots_folder", type=str, default="plots")
    args = parser.parse_args()
    main(args)
