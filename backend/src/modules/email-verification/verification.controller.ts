import type { Request, Response, NextFunction } from "express";

import {
  verifyEmail,
  resendVerificationEmail,
} from "./verification.service.js";

import type {
  VerifyEmailInput,
  ResendVerificationInput,
} from "./verification.types.js";

// Verify email controller
export const verifyEmailController = async (
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> => {
  try {
    await verifyEmail(req.body as VerifyEmailInput);

    res.status(200).json({
      success: true,
      message: "Email verified successfully. You can now log in.",
    });
  } catch (error) {
    next(error);
  }
};

// Resend verification email controller
export const resendVerificationController = async (
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> => {
  try {
    await resendVerificationEmail(
      req.body as ResendVerificationInput
    );

    res.status(200).json({
      success: true,
      message:
        "If the account exists and is not verified, a verification email will be sent.",
    });
  } catch (error) {
    next(error);
  }
};
