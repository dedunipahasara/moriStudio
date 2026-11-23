import type {
  Request,
  Response,
  NextFunction,
} from "express";

import {
  registerUser,
  loginUser,
} from "./auth.service.js";

import type {
  RegisterInput,
  LoginInput,
} from "./auth.types.js";

// Register Controller
export const register = async (
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> => {
  try {
    const data = req.body as RegisterInput;

    const user = await registerUser(data);

    res.status(201).json({
      success: true,
      message: "Registration successful",
      data: {
        user,
      },
    });
  } catch (error) {
    next(error);
  }
};

// Login Controller
export const login = async (
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> => {
  try {
    const data = req.body as LoginInput;

    const result = await loginUser(data);

    res.status(200).json({
      success: true,
      message: "Login successful",
      data: result,
    });
  } catch (error) {
    next(error);
  }
};
