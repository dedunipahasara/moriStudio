import { Router, type Router as ExpressRouter } from "express";

import { authMiddleware } from "../../middleware/auth.middleware.js";
import { validate } from "../../middleware/validation.middleware.js";
import { apiLimiter } from "../../middleware/rate-limit.middleware.js";

import {
  createGenerationController,
  getUserGenerationsController,
  getGenerationByIdController,
} from "./generation.controller.js";

import {
  createGenerationSchema,
  generationListSchema,
  generationIdSchema,
} from "./generation.validation.js";

const router: ExpressRouter = Router();

// All generation routes require authentication
router.use(authMiddleware);

// Create a new generation request
router.post(
  "/",
  apiLimiter,
  validate(createGenerationSchema),
  createGenerationController
);

// Get logged-in user's generation history
router.get(
  "/",
  validate(generationListSchema),
  getUserGenerationsController
);

// Get a specific generation
router.get(
  "/:id",
  validate(generationIdSchema),
  getGenerationByIdController
);

export default router;
