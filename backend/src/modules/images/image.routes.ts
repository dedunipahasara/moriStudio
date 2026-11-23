import { Router, type Router as ExpressRouter } from "express";
import { authMiddleware } from "../../middleware/auth.middleware.js";
import { validate } from "../../middleware/validation.middleware.js";
import { getUserImagesController, getImageByIdController, updateImageController } from "./image.controller.js";
import { imageListSchema, imageIdSchema, updateImageSchema } from "./image.validation.js";

const router: ExpressRouter = Router();
router.use(authMiddleware);
router.get("/", validate(imageListSchema), getUserImagesController);
router.get("/:id", validate(imageIdSchema), getImageByIdController);
router.patch("/:id", validate(updateImageSchema), updateImageController);
export default router;
