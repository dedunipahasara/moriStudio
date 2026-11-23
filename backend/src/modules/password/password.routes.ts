import { Router, type Router as ExpressRouter } from "express";

import { validate } from "../../middleware/validation.middleware.js";
import { authMiddleware } from "../../middleware/auth.middleware.js";

import {
  forgotPasswordLimiter,
  resetPasswordLimiter,
} from "../../middleware/rate-limit.middleware.js";

import {
  forgotPasswordSchema,
  resetPasswordSchema,
  changePasswordSchema,
} from "./password.validation.js";

import {
  forgotPasswordController,
  resetPasswordController,
  changePasswordController,
} from "./password.controller.js";

const router: ExpressRouter = Router();

router.post(
  "/forgot",
  forgotPasswordLimiter,
  validate(forgotPasswordSchema),
  forgotPasswordController
);

router.post(
  "/reset",
  resetPasswordLimiter,
  validate(resetPasswordSchema),
  resetPasswordController
);

router.post(
  "/change",
  authMiddleware,
  validate(changePasswordSchema),
  changePasswordController
);

export default router;
