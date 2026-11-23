import type { Request, Response, NextFunction } from "express";

import {
  getUserProfile,
  updateUserProfile,
} from "./user.service.js";

import type { UpdateUserInput } from "./user.service.js";

// ==========================================
// GET USER PROFILE
// ==========================================

export const getMyProfile = async (
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> => {
  try {
    const user = await getUserProfile(req.user!.userId);

    res.status(200).json({
      success: true,
      message: "User profile retrieved successfully",
      data: {
        user,
      },
    });
  } catch (error) {
    next(error);
  }
};

// ==========================================
// UPDATE USER PROFILE
// ==========================================

export const updateMyProfile = async (
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> => {
  try {
    const user = await updateUserProfile(
      req.user!.userId,
      req.body as UpdateUserInput
    );

    res.status(200).json({
      success: true,
      message: "User profile updated successfully",
      data: {
        user,
      },
    });
  } catch (error) {
    next(error);
  }
};
