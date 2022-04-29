import pandas as pd

from latex import utils as latex_utils
from latex.table_creator import table_creator


def preprocess_df(df):
    latex_utils.convert_adapter_name(df)
    return df


def remove_accuracy_name_multiindex(df):
    accuracy_name = df.columns.levels[0]
    assert len(accuracy_name) == 1
    accuracy_name = accuracy_name[0]
    df = df.droplevel(0, axis=1)
    return df, accuracy_name


def postprocess_df(df):
    df = pd.concat(df, axis=0)
    print(df)
    df = df.pivot(index="adapter", columns="task")
    df, accuracy_name = remove_accuracy_name_multiindex(df)
    df = latex_utils.add_source_only(df, accuracy_name)
    df = latex_utils.shortened_task_names(df)
    df = (df * 100).round(1)
    return df


def best_accuracy_per_adapter(args):
    table_creator(args, "best_accuracy_per_adapter", preprocess_df, postprocess_df)