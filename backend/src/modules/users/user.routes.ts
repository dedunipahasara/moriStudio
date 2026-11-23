import { Router, type Router as ExpressRouter } from "express";

import { authMiddleware } from "../../middleware/auth.middleware.js";
import { validate } from "../../middleware/validation.middleware.js";

import {
  getMyProfile,
  updateMyProfile,
} from "./user.controller.js";

import { updateUserSchema } from "./user.validation.js";

const router: ExpressRouter = Router();

// Get logged-in user's profile
router.get(
  "/me",
  authMiddleware,
  getMyProfile
);

// Update logged-in user's profile
router.patch(
  "/me",
  authMiddleware,
  validate(updateUserSchema),
  updateMyProfile
);

export default router;
