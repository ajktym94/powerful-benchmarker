import pandas as pd

from latex import utils as latex_utils
from latex.predicted_best_acc import (
    get_caption,
    get_preprocess_df,
    interval_fn,
    max_value_fn,
    min_value_fn,
    operation_fn,
    std_condition,
)
from latex.table_creator import table_creator


def get_preprocess_df_wrapper(std=False):
    fn2 = get_preprocess_df(per_adapter=True)

    def fn(df):
        for c in df.columns.levels[0]:
            if std_condition(std, c):
                df = df[c].reset_index()
                break
        return fn2(df)

    return fn


def postprocess_df(df):
    df = pd.concat(df, axis=0).reset_index(drop=True)
    df = latex_utils.rename_validator_args(df)
    df = df.pivot(index=["validator", "validator_args"], columns="task")
    df_dict = {}
    for i in df.columns.levels[0]:
        df_dict[i] = df[i]
    for k, df in df_dict.items():
        df = latex_utils.shortened_task_names(df)
        df = latex_utils.add_mean_std_column(df)
        df = (df * 100).round(1)
        df.columns.names = (None,)
        df.index.names = (None, None)
        df_dict[k] = df
    return df_dict


def caption_hook(caption, k):
    return caption.replace("pair", f"pair for \\textbf{{{k}}}")


def predicted_best_acc_single_adapter(args, topN, threshold):
    basename = f"predicted_best_acc_top{topN}_per_adapter_{threshold}_src_threshold"
    color_map_tag_kwargs = {
        "tag_prefix": latex_utils.get_tag_prefix(basename),
        "min_value_fn": min_value_fn,
        "max_value_fn": max_value_fn,
        "num_steps": 11,
        "interval_fn": interval_fn,
        "operation_fn": operation_fn,
    }

    caption = get_caption(
        topN, threshold, per_adapter=False, with_equation_ref=False, short_caption=True
    )

    highlight_max_subset = list(latex_utils.shortened_task_name_dict().values()) + [
        "Mean"
    ]

    table_creator(
        args,
        basename,
        get_preprocess_df_wrapper(std=False),
        postprocess_df,
        color_map_tag_kwargs,
        add_resizebox=True,
        clines="skip-last;data",
        caption=caption,
        highlight_min=True,
        highlight_max_subset=highlight_max_subset,
        highlight_min_subset=["Std"],
        final_str_hook=latex_utils.validator_final_str_hook,
        caption_hook=caption_hook,
        position="H",
    )
