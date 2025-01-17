import pandas as pd

from powerful_benchmarker.utils import score_utils
from validator_tests.utils import df_utils


def shortened_task_name_dict():
    return {
        "mnist_mnist_mnistm": "MM",
        "office31_amazon_dslr": "AD",
        "office31_amazon_webcam": "AW",
        "office31_dslr_amazon": "DA",
        "office31_dslr_webcam": "DW",
        "office31_webcam_amazon": "WA",
        "office31_webcam_dslr": "WD",
        "officehome_art_clipart": "AC",
        "officehome_art_product": "AP",
        "officehome_art_real": "AR",
        "officehome_clipart_art": "CA",
        "officehome_clipart_product": "CP",
        "officehome_clipart_real": "CR",
        "officehome_product_art": "PA",
        "officehome_product_clipart": "PC",
        "officehome_product_real": "PR",
        "officehome_real_art": "RA",
        "officehome_real_clipart": "RC",
        "officehome_real_product": "RP",
    }


def shortened_task_names(df):
    return df.rename(columns=shortened_task_name_dict())


def convert_adapter_name(df):
    df["adapter"] = df["adapter"].str.replace("Config", "")


def convert_adapter_column_names(df):
    df.columns = df.columns.str.replace("Config", "")


# assumes datasets are ordered MNIST, Office31, OfficeHome
def add_dataset_multiindex_column(df):
    new_cols = []
    for full_name, short_name in shortened_task_name_dict().items():
        if full_name.startswith("mnist"):
            top_level = ""
        elif full_name.startswith("office31"):
            top_level = "Office31"
        elif full_name.startswith("officehome"):
            top_level = "OfficeHome"
        new_cols.append((top_level, short_name))

    df.columns = pd.MultiIndex.from_tuples(new_cols)


def add_source_only(df, accuracy_name):
    cols = df.columns.values
    _, split, average = df_utils.accuracy_name_split(accuracy_name)
    tasks_split = [df_utils.task_name_split(x) for x in cols]
    src_only_accs = [
        score_utils.pretrained_target_accuracy(
            dataset, [src_domains], [target_domains], split, average
        )
        for dataset, src_domains, target_domains in tasks_split
    ]
    src_only_accs = pd.DataFrame(
        {x: y for x, y in zip(cols, src_only_accs)}, index=["Source only"]
    )
    return pd.concat([src_only_accs, df], axis=0)


def resizebox(x):
    x = x.replace("\\begin{tabular}", "\\resizebox{\\textwidth}{!}{\\begin{tabular}")
    x = x.replace("\\end{tabular}", "\\end{tabular}}")
    return x


# assuming unified validator/validator_args
def validators_to_remove():
    return [
        "Accuracy_average_macro_split_src_train",
        "Accuracy_average_macro_split_src_val",
        "Accuracy_average_macro_split_target_train",
        "Accuracy_average_macro_split_target_val",
        "Accuracy_average_micro_split_target_train",
        "Accuracy_average_micro_split_target_val",
        "BNM_layer_features_split_src_train",
        "BNM_layer_features_split_src_val",
        "BNM_layer_features_split_target_train",
        "BNM_layer_preds_split_src_train",
        "BNM_layer_preds_split_src_val",
        "BNM_layer_preds_split_target_train",
        "BNMSummed_layer_features",
        "BNMSummed_layer_preds",
        "BNMSummedSrcVal_layer_features",
        "BNMSummedSrcVal_layer_preds",
        "ClassAMICentroidInit_layer_features_normalize_True_p_2.0_split_train_with_src_True",
        "ClassAMICentroidInit_layer_logits_normalize_True_p_2.0_split_train_with_src_True",
        "ClassAMICentroidInit_layer_features_normalize_True_p_2.0_split_train_with_src_False",
        "ClassAMICentroidInit_layer_logits_normalize_True_p_2.0_split_train_with_src_False",
        "Diversity_split_src_train",
        "Diversity_split_src_val",
        "Diversity_split_target_train",
        "DiversitySummed",
        "MMD_exponent_0_layer_features_normalize_True_split_train",
        "MMD_exponent_0_layer_logits_normalize_True_split_train",
        "MMD_exponent_0_layer_preds_normalize_True_split_train",
        "MMDPerClass_exponent_0_layer_features_normalize_True_split_train",
        "MMDPerClass_exponent_0_layer_logits_normalize_True_split_train",
        "MMDPerClass_exponent_0_layer_preds_normalize_False_split_train",
        "MMDPerClass_exponent_0_layer_preds_normalize_True_split_train",
        "NegSND_T_0.01_layer_features_split_target_train",
        "NegSND_T_0.05_layer_features_split_target_train",
        "NegSND_T_0.1_layer_features_split_target_train",
        "NegSND_T_0.5_layer_features_split_target_train",
        "NegSND_T_0.01_layer_logits_split_target_train",
        "NegSND_T_0.05_layer_logits_split_target_train",
        "NegSND_T_0.1_layer_logits_split_target_train",
        "NegSND_T_0.5_layer_logits_split_target_train",
        "NegSND_T_0.01_layer_preds_split_target_train",
        "NegSND_T_0.05_layer_preds_split_target_train",
        "NegSND_T_0.1_layer_preds_split_target_train",
        "NegSND_T_0.5_layer_preds_split_target_train",
        "SND_T_0.01_layer_features_split_target_train",
        "SND_T_0.01_layer_logits_split_target_train",
        "SND_T_0.01_layer_preds_split_target_train",
    ]


def filter_validators(df):
    df = df_utils.unify_validator_columns(
        df, new_col_name="unified_validator", drop_validator_args=False
    )
    df = df.reset_index(drop=True)
    df = df.drop(df[df.unified_validator.isin(validators_to_remove())].index, axis=0)
    return df.drop(columns=["unified_validator"])


def get_tag_prefix(basename):
    num_to_word = [
        "zero",
        "one",
        "two",
        "three",
        "four",
        "five",
        "six",
        "seven",
        "eight",
        "nine",
    ]
    basename = basename.replace("_", "").replace(".", "")
    for i in range(10):
        basename = basename.replace(str(i), num_to_word[i])
    return basename


def pretty_validator_args_dict():
    return {
        "average micro split src train": "Source Train",
        "average micro split src val": "Source Val",
        "layer logits split src train": "Source Train",
        "layer logits split src val": "Source Val",
        "layer logits split target train": "Target",
        "layer features normalize False p 2.0 split train with src False": "Target Features",
        "layer features normalize False p 2.0 split train with src True": "Source + Target Features",
        "layer logits normalize False p 2.0 split train with src False": "Target Logits",
        "layer logits normalize False p 2.0 split train with src True": "Source + Target Logits",
        "layer features normalize True p 2.0 split train with src False": "Target Features, L2 Normalized",
        "layer features normalize True p 2.0 split train with src True": "Source + Target Features, L2 Normalized",
        "layer logits normalize True p 2.0 split train with src False": "Target Logits, L2 Normalized",
        "layer logits normalize True p 2.0 split train with src True": "Source + Target Logits, L2 Normalized",
        "layer features normalization None": "Features",
        "layer features normalization max": "Features, max normalization",
        "layer features normalization standardize": "Features, standardization",
        "layer logits normalization None": "Logits",
        "layer logits normalization max": "Logits, max normalization",
        "layer logits normalization standardize": "Logits, standardization",
        "layer preds normalization None": "Preds",
        "layer preds normalization max": "Preds, max normalization",
        "layer preds normalization standardize": "Preds, standardization",
        "split src train": "Source Train",
        "split src val": "Source Val",
        "split target train": "Target",
        "exponent 0 layer features normalize False split train": "Features",
        "exponent 0 layer features normalize True split train": "Features, L2 Normalized",
        "exponent 0 layer logits normalize False split train": "Logits",
        "exponent 0 layer logits normalize True split train": "Logits, L2 Normalized",
        "exponent 0 layer preds normalize False split train": "Preds",
        "exponent 0 layer preds normalize True split train": "Preds, L2 Normalized",
        "T 0.01 layer features split target train": "Features, \\tau=0.01",
        "T 0.01 layer logits split target train": "Logits, \\tau=0.01",
        "T 0.01 layer preds split target train": "Preds, \\tau=0.01",
        "T 0.05 layer features split target train": "Features, \\tau=0.05",
        "T 0.05 layer logits split target train": "Logits, \\tau=0.05",
        "T 0.05 layer preds split target train": "Preds, \\tau=0.05",
        "T 0.1 layer features split target train": "Features, \\tau=0.1",
        "T 0.1 layer logits split target train": "Logits, \\tau=0.1",
        "T 0.1 layer preds split target train": "Preds, \\tau=0.1",
        "T 0.5 layer features split target train": "Features, \\tau=0.5",
        "T 0.5 layer logits split target train": "Logits, \\tau=0.5",
        "T 0.5 layer preds split target train": "Preds, \\tau=0.5",
    }


def pretty_validator_dict():
    return {
        "BNMSummed": "BNM",
        "BNMSummedSrcVal": "BNM",
        "ClassAMICentroidInit": "ClassAMI",
        "DEVBinary": "DEV",
        "EntropySummed": "Entropy",
        "EntropySummedSrcVal": "Entropy",
        "IMSummed": "IM",
        "IMSummedSrcVal": "IM",
    }


def rename_specific_validator_args(df):
    df.loc[df["validator"] == "BNMSummed", "validator_args"] = "Source Train + Target"
    df.loc[
        df["validator"] == "BNMSummedSrcVal", "validator_args"
    ] = "Source Val + Target"
    df.loc[
        df["validator"] == "EntropySummed", "validator_args"
    ] = "Source Train + Target"
    df.loc[
        df["validator"] == "EntropySummedSrcVal", "validator_args"
    ] = "Source Val + Target"
    df.loc[df["validator"] == "IMSummed", "validator_args"] = "Source Train + Target"
    df.loc[
        df["validator"] == "IMSummedSrcVal", "validator_args"
    ] = "Source Val + Target"
    df.loc[
        (
            (df["validator_args"].str.contains("max normalization"))
            | (df["validator_args"].str.contains("standardization"))
        )
        & (df["validator"] == "DEVBinary"),
        "validator",
    ] = "DEVN"


def rename_validator_args(df):
    df.validator_args.replace(to_replace=pretty_validator_args_dict(), inplace=True)
    rename_specific_validator_args(df)
    df.validator.replace(to_replace=pretty_validator_dict(), inplace=True)
    return df


def add_mean_std_column(df):
    df = df.assign(Mean=df.mean(axis=1, skipna=False))
    df = df.assign(Std=df.std(axis=1, skipna=False))
    return df


def adapter_names():
    return ["ATDOC", "BNM", "BSP", "CDAN", "DANN", "GVB", "IM", "MCC", "MCD", "MMD"]


def adapter_final_str_hook(x):
    old = (
        "\\resizebox{\\textwidth}{!}{\\begin{tabular}{lrrrrrrrrrrrrrrrrrrr}\n\\toprule"
    )
    new = "\\resizebox{\\textwidth}{!}{\\begin{tabular}{lr|rrrrrr|rrrrrrrrrrrr}\n\\toprule\n & \\multicolumn{1}{c|}{} & \\multicolumn{6}{c|}{Office31} & \\multicolumn{12}{c}{OfficeHome} \\\\"
    return x.replace(old, new)


def validator_per_adapter_final_str_hook(x):
    old = "\\resizebox{\\textwidth}{!}{\\begin{tabular}{llrrrrrrrrrrrr}\n\\toprule"
    new = "\\resizebox{\\textwidth}{!}{\\begin{tabular}{llrrrrrrrrrr|rr}\n\\toprule"
    return x.replace(old, new)


def validator_final_str_hook(x):
    old = "\\resizebox{\\textwidth}{!}{\\begin{tabular}{llrrrrrrrrrrrrrrrrrrrrr}\n\\toprule"
    new = "\\resizebox{\\textwidth}{!}{\\begin{tabular}{llr|rrrrrr|rrrrrrrrrrrr|rr}\n\\toprule\n & & \\multicolumn{1}{c|}{} & \\multicolumn{6}{c|}{Office31} & \\multicolumn{12}{c|}{OfficeHome} & & \\\\"
    return x.replace(old, new)
