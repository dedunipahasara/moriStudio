import type {
  Request,
  Response,
  NextFunction,
  RequestHandler,
} from "express";

import type { ZodType } from "zod";

export const validate = (schema: ZodType): RequestHandler => {
  return (
    req: Request,
    res: Response,
    next: NextFunction
  ): void => {
    const result = schema.safeParse({
      body: req.body,
      query: req.query,
      params: req.params,
    });

    if (!result.success) {
      const errors = result.error.issues.map((issue) => ({
        field: issue.path.join("."),
        message: issue.message,
      }));

      res.status(400).json({
        success: false,
        message: "Validation failed",
        errors,
      });

      return;
    }

    next();
  };
};
