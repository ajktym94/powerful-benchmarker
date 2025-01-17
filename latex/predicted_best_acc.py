import re

import numpy as np
import pandas as pd

from latex import utils as latex_utils
from latex.color_map_tags import default_interval_fn, reverse_interval_fn
from latex.table_creator import table_creator
from validator_tests.utils.utils import validator_args_delimited


def std_condition(std, c):
    endwith_std = c.endswith("_std")
    return (std and endwith_std) or (not std and not endwith_std)


def get_preprocess_df(per_adapter):
    def fn(df):
        df = latex_utils.filter_validators(df)
        df["validator_args"] = df.apply(
            lambda x: validator_args_delimited(
                x["validator_args"], delimiter=" "
            ).replace("_", " "),
            axis=1,
        )
        if per_adapter:
            latex_utils.convert_adapter_column_names(df)
        return df

    return fn


def get_postprocess_df(per_adapter):
    def fn(df):
        df = pd.concat(df, axis=0).reset_index(drop=True)
        df = latex_utils.rename_validator_args(df)
        if per_adapter:
            df = df.groupby(["validator", "validator_args"], dropna=False).agg(np.mean)
        else:
            df = df.pivot(index=["validator", "validator_args"], columns="task")
            df = df.droplevel(0, axis=1)
            df = latex_utils.shortened_task_names(df)
        df = latex_utils.add_mean_std_column(df)
        df = (df * 100).round(1)
        df.columns.names = (None,)
        df.index.names = (None, None)
        return df

    return fn


def get_preprocess_df_wrapper(per_adapter, std=False):
    fn2 = get_preprocess_df(per_adapter)

    def fn(df):

        if per_adapter:
            for c in df.columns.levels[0]:
                if std_condition(std, c):
                    df = df[c].reset_index()
                    break
        else:
            columns = []
            for c in df.columns:
                if (not c.startswith("predicted_best_acc")) or std_condition(std, c):
                    columns.append(c)
            df = df[columns]
        return fn2(df)

    return fn


def interval_fn(min_value, max_value, num_steps, column_name):
    if column_name == "Std":
        return reverse_interval_fn(min_value, max_value, num_steps, column_name)
    return default_interval_fn(min_value, max_value, num_steps, column_name)


def operation_fn(lower_bound, column_name):
    if column_name == "Std":
        return "<"
    return ">"


def min_value_fn(curr_df, column_name):
    if column_name == "Std":
        return curr_df.min()
    return curr_df.loc[("Accuracy", "Source Val")]


def max_value_fn(curr_df, column_name):
    if column_name == "Std":
        return curr_df.loc[("Accuracy", "Source Val")]
    return curr_df.max()


def get_highlight_max_subset(per_adapter):
    if per_adapter:
        highlight_max_subset = latex_utils.adapter_names()
    else:
        highlight_max_subset = list(latex_utils.shortened_task_name_dict().values())
    highlight_max_subset += ["Mean"]
    return highlight_max_subset


def get_final_str_hook(per_adapter):
    return (
        latex_utils.validator_per_adapter_final_str_hook
        if per_adapter
        else latex_utils.validator_final_str_hook
    )


def remove_whitespace_before_punctuation(x):
    return re.sub('\s+([?.!",](?:\s|$))', r"\1", x)


def get_caption(
    topN, threshold, per_adapter, with_equation_ref=True, short_caption=False
):
    threshold_str = int(threshold * 100)
    equation_ref = ""
    if threshold_str == 0:
        threshold_phrase = f", without removing any checkpoints"
    else:
        threshold_phrase = f", after removing checkpoints with < {threshold_str}\% RSVA"
    if with_equation_ref:
        if per_adapter:
            equation_ref = "(see equations \\ref{AverageTop20RTA_equation} and \\ref{RSVA_equation})"
        else:
            equation_ref = (
                "(see equations \\ref{TopN_RTA_equation} and \\ref{RSVA_equation})"
            )

    if per_adapter:
        caption = f"The Average Top {topN} RTA of each validator/algorithm pair {threshold_phrase} {equation_ref}."
    else:
        caption = f"The Top {topN} RTA of each validator/task pair {threshold_phrase} {equation_ref}."

    if not short_caption:
        mean_std_str = "algorithm" if per_adapter else "task"
        caption += (
            " Green cells have better performance than the Source Val Accuracy validator. "
            f"The best value per column is bolded. The Mean and Std columns are the mean and standard deviation of all {mean_std_str} columns."
        )

    # https://stackoverflow.com/a/18878970
    return remove_whitespace_before_punctuation(caption)


def predicted_best_acc(args, topN, threshold, per_adapter=False):
    per_adapter_str = "per_adapter_" if per_adapter else ""
    basename = (
        f"predicted_best_acc_top{topN}_{per_adapter_str}{threshold}_src_threshold"
    )
    color_map_tag_kwargs = {
        "tag_prefix": latex_utils.get_tag_prefix(basename),
        "min_value_fn": min_value_fn,
        "max_value_fn": max_value_fn,
        "num_steps": 11,
        "interval_fn": interval_fn,
        "operation_fn": operation_fn,
    }

    caption = get_caption(topN, threshold, per_adapter)
    highlight_max_subset = get_highlight_max_subset(per_adapter)
    final_str_hook = get_final_str_hook(per_adapter)

    table_creator(
        args,
        basename,
        get_preprocess_df_wrapper(per_adapter),
        get_postprocess_df(per_adapter),
        color_map_tag_kwargs,
        add_resizebox=True,
        clines="skip-last;data",
        caption=caption,
        highlight_min=True,
        highlight_max_subset=highlight_max_subset,
        highlight_min_subset=["Std"],
        final_str_hook=final_str_hook,
    )
