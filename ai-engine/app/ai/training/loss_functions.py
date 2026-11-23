import torch.nn.functional as F


def noise_prediction_loss(
    predicted_noise,
    actual_noise,
    loss_type="mse",
):
    if loss_type == "mse":
        return F.mse_loss(predicted_noise, actual_noise)

    if loss_type == "l1":
        return F.l1_loss(predicted_noise, actual_noise)

    if loss_type == "huber":
        return F.smooth_l1_loss(predicted_noise, actual_noise)

    raise ValueError(f"Unsupported loss type: {loss_type}")


def reconstruction_loss(predicted_images, target_images):
    return F.l1_loss(predicted_images, target_images)


def combined_loss(
    predicted_noise,
    actual_noise,
    predicted_images=None,
    target_images=None,
    reconstruction_weight=0.1,
):
    noise_loss = noise_prediction_loss(
        predicted_noise,
        actual_noise,
    )

    if predicted_images is None or target_images is None:
        return noise_loss

    image_loss = reconstruction_loss(
        predicted_images,
        target_images,
    )

    return noise_loss + reconstruction_weight * image_loss
