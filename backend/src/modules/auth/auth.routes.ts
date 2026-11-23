import { Router, type Router as ExpressRouter } from "express";

import { validate } from "../../middleware/validation.middleware.js";

import {
  loginLimiter,
  registerLimiter,
} from "../../middleware/rate-limit.middleware.js";

import {
  registerSchema,
  loginSchema,
} from "./auth.validation.js";

import {
  register,
  login,
} from "./auth.controller.js";

const router: ExpressRouter = Router();

router.post(
  "/register",
  registerLimiter,
  validate(registerSchema),
  register
);

router.post(
  "/login",
  loginLimiter,
  validate(loginSchema),
  login
);

export default router;
