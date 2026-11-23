import torch


def create_optimizer(
    model,
    prompt_encoder,
    text_feature_extractor,
    learning_rate=1e-4,
    weight_decay=1e-5,
):
    parameters = (
        list(model.parameters())
        + list(prompt_encoder.parameters())
        + list(text_feature_extractor.parameters())
    )

    return torch.optim.AdamW(
        parameters,
        lr=learning_rate,
        weight_decay=weight_decay,
    )