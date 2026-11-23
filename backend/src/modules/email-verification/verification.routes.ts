import { Router, type Router as ExpressRouter } from "express";

import { validate } from "../../middleware/validation.middleware.js";
import { verificationLimiter } from "../../middleware/rate-limit.middleware.js";

import {
  verifyEmailController,
  resendVerificationController,
} from "./verification.controller.js";

import { z } from "zod";

const router: ExpressRouter = Router();

const verifyEmailSchema = z.object({
  body: z.object({
    token: z.string().min(1, "Verification token is required"),
  }),
});

const resendVerificationSchema = z.object({
  body: z.object({
    email: z.string().trim().email("Invalid email address").toLowerCase(),
  }),
});

router.post(
  "/verify",
  verificationLimiter,
  validate(verifyEmailSchema),
  verifyEmailController
);

router.post(
  "/resend",
  verificationLimiter,
  validate(resendVerificationSchema),
  resendVerificationController
);

export default router;
