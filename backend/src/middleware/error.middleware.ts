import type {
  Request,
  Response,
  NextFunction,
  ErrorRequestHandler,
} from "express";

import { env } from "../config/env.js";

export const errorMiddleware: ErrorRequestHandler = (
  err: Error & { statusCode?: number },
  _req: Request,
  res: Response,
  _next: NextFunction
): void => {
  console.error("API Error:", err);

  const statusCode =
    typeof err.statusCode === "number"
      ? err.statusCode
      : 500;

  const message =
    statusCode === 500 && env.NODE_ENV === "production"
      ? "Internal server error"
      : err.message || "Something went wrong";

  res.status(statusCode).json({
    success: false,
    message,
    ...(env.NODE_ENV === "development" && {
      stack: err.stack,
    }),
  });
};
