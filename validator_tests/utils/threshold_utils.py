import numpy as np
import pandas as pd
import tqdm

from powerful_benchmarker.utils.score_utils import (
    pretrained_src_val_accuracy,
    pretrained_target_train_accuracy,
)

BASE_GROUP_BY = ["validator", "validator_args"]
TARGET_ACCURACY = "target_train_macro"


def filter_by_acc(df, min_acc, domain_type):
    if domain_type == "src":
        split = "val"
    elif domain_type == "target":
        split = "train"
    return df[df[f"{domain_type}_{split}_macro"] > min_acc]


def domain_type_str(domain_type):
    return "_".join(domain_type)


def per_threshold(df, pretrained_acc, domain_type, fn):
    print("pretrained_acc", pretrained_acc)
    all_df = []
    upper_bound = 2
    thresholds = np.linspace(0, upper_bound, 201)
    thresholds = np.insert(thresholds, 0, -0.01)
    for threshold in tqdm.tqdm(thresholds):
        min_acc = [pa * threshold for pa in pretrained_acc]
        curr_df = df
        for i, k in enumerate(domain_type):
            curr_df = filter_by_acc(curr_df, np.round(min_acc[i], 4), k)
        if len(curr_df) == 0:
            continue
        if threshold < 0:
            assert len(curr_df) == len(df)
        t_str = f"{domain_type_str(domain_type)}_threshold"
        curr_df = fn(curr_df)
        curr_df = curr_df.assign(**{t_str: threshold})
        curr_df = curr_df.round({t_str: 2})
        all_df.append(curr_df)
    return pd.concat(all_df, axis=0, ignore_index=True)


def get_per_src_threshold(df, dataset, src_domain, fn):
    pretrained_acc = pretrained_src_val_accuracy(dataset, src_domain)
    return per_threshold(df, [pretrained_acc], ["src"], fn)


def get_per_target_threshold(df, dataset, source_domain, target_domain, fn):
    pretrained_acc = pretrained_target_train_accuracy(
        dataset, source_domain, target_domain
    )
    return per_threshold(df, [pretrained_acc], ["target"], fn)


def get_per_threshold(df, fn):
    all_per_src, all_per_target, all_per_src_target = [], [], []
    for dataset in df["dataset"].unique():
        for src_domains in df["src_domains"].unique():
            for target_domains in df["target_domains"].unique():
                curr_df = df[
                    (df["dataset"] == dataset)
                    & (df["src_domains"] == src_domains)
                    & (df["target_domains"] == target_domains)
                ]
                per_src = get_per_src_threshold(curr_df, dataset, src_domains, fn)
                per_target = get_per_target_threshold(
                    curr_df, dataset, src_domains, target_domains, fn
                )
                all_per_src.append(per_src)
                all_per_target.append(per_target)
    all_per_src = pd.concat(all_per_src, axis=0, ignore_index=True)
    all_per_target = pd.concat(all_per_target, axis=0, ignore_index=True)
    return all_per_src, all_per_target


def get_corr(group_by):
    def fn(df):
        curr_df = (
            df.groupby(group_by)[["score", TARGET_ACCURACY]]
            .corr(method="spearman")
            .iloc[0::2, -1]
        )
        return (
            curr_df.reset_index()
            .drop([f"level_{len(group_by)}"], axis=1)
            .rename(columns={TARGET_ACCURACY: "correlation"})
            .dropna()
        )

    return fn


def get_predicted_best_acc(group_by, nlargest):
    def fn(df):
        return get_avg_top_n_acc_by_group(
            df, group_by, nlargest, "score", "predicted_best_acc"
        )

    return fn


def get_all(group_by, nlargest):
    corr_fn = get_corr(group_by)
    acc_fn = get_predicted_best_acc(group_by, nlargest)

    def fn(df):
        df1 = corr_fn(df)
        df2 = acc_fn(df)
        return df1.merge(df2, on=group_by)

    return fn


def group_by_task():
    return BASE_GROUP_BY + ["dataset", "src_domains", "target_domains"]


def group_by_task_adapter():
    return group_by_task() + ["adapter"]


def get_all_per_task(nlargest):
    return get_all(group_by_task(), nlargest)


def get_all_per_task_per_adapter(nlargest):
    return get_all(group_by_task_adapter(), nlargest)


def get_avg_top_n_acc_by_group(df, group_by, nlargest, sort_by, new_col_name):
    top_scores = df.groupby(group_by)[sort_by].nlargest(nlargest)
    top_idx = top_scores.index.get_level_values(len(group_by))
    df = df.loc[top_idx]
    return df.groupby(group_by)[TARGET_ACCURACY].mean().reset_index(name=new_col_name)


def convert_predicted_best_acc_to_rel(df, per_x, per_adapter, nlargest):
    group_by = group_by_task_adapter() if per_adapter else group_by_task()
    best_acc = get_avg_top_n_acc_by_group(
        df, group_by, nlargest, TARGET_ACCURACY, "best_acc"
    )
    per_x = per_x.merge(best_acc, on=group_by)
    per_x["predicted_best_acc"] = per_x["predicted_best_acc"] / per_x["best_acc"]
    return per_x
