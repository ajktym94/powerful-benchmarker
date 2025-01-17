import os

import h5py
import numpy as np
from pytorch_adapt.utils import common_functions as c_f


class SaveFeatures:
    def __init__(self, folder, logger):
        self.folder = os.path.join(folder, "features")
        c_f.makedir_if_not_there(self.folder)
        self.logger = logger
        self.required_data = [
            "src_train",
            "src_val",
            "target_train_with_labels",
            "target_val_with_labels",
        ]

    def __call__(self, epoch, **collected_data):
        if epoch == 0:
            return

        inference_dict = {}
        for k, v in collected_data.items():
            curr_k = k.replace("_with_labels", "")
            inference_dict[curr_k] = {
                name: v[name].cpu().numpy()
                for name in v.keys()
                if name not in discard_keys()
            }

        losses_dict = self.logger.get_losses()

        with h5py.File(os.path.join(self.folder, "features.hdf5"), "a") as hf:
            write_nested_dict(hf, inference_dict, epoch, "inference")
            write_nested_dict(hf, losses_dict, epoch, "losses")


class SaveFeaturesATDOC(SaveFeatures):
    def __init__(self, atdoc, **kwargs):
        super().__init__(**kwargs)
        self.atdoc = atdoc

    def __call__(self, epoch, **collected_data):
        super().__call__(epoch, **collected_data)
        atdoc_dict = {
            "target_train": {
                "feat_memory": self.atdoc.labeler.feat_memory.cpu().numpy(),
                "pred_memory": self.atdoc.labeler.pred_memory.cpu().numpy(),
            }
        }
        with h5py.File(os.path.join(self.folder, "features.hdf5"), "a") as hf:
            write_nested_dict(hf, atdoc_dict, epoch, "atdoc")


def save_features_atdoc(atdoc):
    def fn(folder, logger):
        return SaveFeaturesATDOC(atdoc, folder=folder, logger=logger)

    return fn


def write_nested_dict(hf, d, epoch, series_name):
    for k1, v1 in d.items():
        grp = hf.create_group(f"{epoch}/{series_name}/{k1}")
        for k2, v2 in v1.items():
            kwargs = (
                {"compression": "gzip"} if isinstance(v2, (np.ndarray, list)) else {}
            )
            grp.create_dataset(k2, data=v2, **kwargs)


def discard_keys():
    return ["imgs", "domain", "preds"]
