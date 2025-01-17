import os

import matplotlib.pyplot as plt
import seaborn as sns
from pytorch_adapt.utils import common_functions as c_f

from .plot_utils import plot_loop


def multiplot(
    plots_folder,
    df,
    x,
    y,
    filename,
    plot_fn,
    hue=None,
    rotation=0,
    order=None,
    xlim=None,
    ylim=None,
    other_kwargs=None,
    show_x_label=False,
):
    sns.set(font_scale=2, style="whitegrid", rc={"figure.figsize": (12.8, 9.6)})
    kwargs = {"data": df, "x": x, "y": y, "hue": hue}
    if order is not None:
        kwargs.update({"order": order})
    if other_kwargs:
        kwargs.update(other_kwargs)
    plot = plot_fn(**kwargs)
    plot.legend(loc="center left", bbox_to_anchor=(1, 0.5), title=hue)
    if not show_x_label:
        plot.set(xlabel="")
    plt.setp(plot.get_xticklabels(), rotation=rotation)
    if xlim:
        plt.xlim(*xlim)
    if ylim:
        plt.ylim(*ylim)
    fig = plot.get_figure()
    c_f.makedir_if_not_there(plots_folder)
    fig.savefig(
        os.path.join(plots_folder, f"{filename}.png"),
        bbox_inches="tight",
    )
    fig.clf()


def per_validator_args(x, y):
    def fn(curr_plots_folder, curr_df, filename):
        multiplot(
            curr_plots_folder,
            curr_df,
            x,
            y,
            filename,
            sns.lineplot,
            "validator_args",
        )

    return fn


def plot_corr_vs_X(threshold_type, per_adapter):
    def fn(df, plots_folder):
        plots_folder = os.path.join(plots_folder, f"corr_vs_{threshold_type}")

        filter_by = ["adapter", "validator"] if per_adapter else ["validator"]

        plot_loop(
            df,
            plots_folder,
            per_validator_args(f"{threshold_type}_threshold", "correlation"),
            filter_by=filter_by,
            sub_folder_components=[],
            filename_components=filter_by,
            per_adapter=per_adapter,
        )

    return fn


def plot_predicted_best_acc_vs_X(threshold_type, per_adapter):
    def fn(df, plots_folder):
        plots_folder = os.path.join(
            plots_folder, f"predicted_best_acc_vs_{threshold_type}"
        )

        filter_by = ["adapter", "validator"] if per_adapter else ["validator"]

        plot_loop(
            df,
            plots_folder,
            per_validator_args(f"{threshold_type}_threshold", "predicted_best_acc"),
            filter_by=filter_by,
            sub_folder_components=[],
            filename_components=filter_by,
            per_adapter=per_adapter,
        )

    return fn
