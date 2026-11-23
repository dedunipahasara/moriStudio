from PIL import Image, ImageOps


class ImageResizer:

    def resize(
        self,
        image,
        width,
        height,
        maintain_aspect_ratio=True,
    ):
        if not isinstance(image, Image.Image):
            raise TypeError("Input must be a PIL Image.")

        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive.")

        if maintain_aspect_ratio:
            return ImageOps.contain(
                image,
                (width, height),
                method=Image.Resampling.LANCZOS,
            )

        return image.resize(
            (width, height),
            Image.Resampling.LANCZOS,
        )

    def resize_and_crop(self, image, width, height):
        if not isinstance(image, Image.Image):
            raise TypeError("Input must be a PIL Image.")

        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive.")

        return ImageOps.fit(
            image,
            (width, height),
            method=Image.Resampling.LANCZOS,
            centering=(0.5, 0.5),
        )

    def create_thumbnail(self, image, max_size=(256, 256)):
        if not isinstance(image, Image.Image):
            raise TypeError("Input must be a PIL Image.")

        if max_size[0] <= 0 or max_size[1] <= 0:
            raise ValueError(
                "Thumbnail dimensions must be positive."
            )

        thumbnail = image.copy()

        thumbnail.thumbnail(
            max_size,
            Image.Resampling.LANCZOS,
        )

        return thumbnail

    def get_aspect_ratio(self, image):
        if not isinstance(image, Image.Image):
            raise TypeError("Input must be a PIL Image.")

        return round(image.width / image.height, 4)