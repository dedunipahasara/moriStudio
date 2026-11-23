
import type { Request, Response, NextFunction, RequestHandler } from "express";
import jwt from "jsonwebtoken";

import { env } from "../config/env.js";
import { AppError } from "../utils/app-error.js";

export interface AuthenticatedUser {
  userId: string;
  email: string;
}

export const authMiddleware: RequestHandler = (
  req: Request,
  _res: Response,
  next: NextFunction
): void => {
  try {
    const authorization = req.headers.authorization;

    if (!authorization || !authorization.startsWith("Bearer ")) {
      throw new AppError("Authentication token is required", 401);
    }

    const token = authorization.split(" ")[1];

    if (!token) {
      throw new AppError("Invalid authentication token", 401);
    }

    const decoded = jwt.verify(token, env.JWT_SECRET);

    if (
      typeof decoded === "string" ||
      typeof decoded.userId !== "string" ||
      typeof decoded.email !== "string"
    ) {
      throw new AppError("Invalid authentication token", 401);
    }

    req.user = {
      userId: decoded.userId,
      email: decoded.email,
    };

    next();
  } catch (error) {
    if (error instanceof AppError) {
      next(error);
      return;
    }

    if (
      error instanceof jwt.TokenExpiredError ||
      error instanceof jwt.JsonWebTokenError
    ) {
      next(new AppError("Invalid or expired token", 401));
      return;
    }

    next(error);
  }
};
