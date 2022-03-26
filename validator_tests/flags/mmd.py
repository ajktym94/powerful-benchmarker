def MMD():
    flags = []
    for layer in ["features", "logits", "preds"]:
        for exponent in [0, 8]:
            for normalize in [0, 1]:
                flags.append(
                    {
                        "validator": "MMD",
                        "split": "train",
                        "layer": layer,
                        "exponent": str(exponent),
                        "normalize": str(normalize),
                    }
                )
    return flags