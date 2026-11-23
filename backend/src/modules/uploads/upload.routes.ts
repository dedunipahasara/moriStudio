import { Router } from "express";

import { uploadImage } from "./upload.validation.js";
import { uploadImageController } from "./upload.controller.js";
import { authMiddleware } from "../../middleware/auth.middleware.js";

const router = Router();

// Upload reference image
router.post(
  "/image",
  authMiddleware,
  uploadImage.single("image"),
  uploadImageController
);

export default router;
