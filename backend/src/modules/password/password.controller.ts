import type { Request, Response, NextFunction } from "express";

import {
  forgotPassword,
  resetPassword,
  changePassword,
} from "./password.service.js";

import type {
  ForgotPasswordInput,
  ResetPasswordInput,
  ChangePasswordInput,
} from "./password.types.js";

export const forgotPasswordController = async (
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> => {
  try {
    await forgotPassword(req.body as ForgotPasswordInput);

    res.status(200).json({
      success: true,
      message: "If the email is registered, a password reset link will be sent.",
    });
  } catch (error) {
    next(error);
  }
};

export const resetPasswordController = async (
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> => {
  try {
    await resetPassword(req.body as ResetPasswordInput);

    res.status(200).json({
      success: true,
      message: "Password reset successful. Please log in.",
    });
  } catch (error) {
    next(error);
  }
};

export const changePasswordController = async (
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> => {
  try {
    await changePassword(
      req.user!.userId,
      req.body as ChangePasswordInput
    );

    res.status(200).json({
      success: true,
      message: "Password changed successfully",
    });
  } catch (error) {
    next(error);
  }
};
