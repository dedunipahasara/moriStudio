import { z } from "zod";

export const forgotPasswordSchema = z.object({
  body: z.object({
    email: z.string().trim().email("Invalid email address").toLowerCase(),
  }),
});

export const resetPasswordSchema = z.object({
  body: z.object({
    token: z.string().min(1, "Reset token is required"),
    newPassword: z
      .string()
      .min(8, "Password must contain at least 8 characters")
      .max(128, "Password cannot exceed 128 characters"),
  }),
});

export const changePasswordSchema = z.object({
  body: z.object({
    currentPassword: z.string().min(1, "Current password is required"),
    newPassword: z
      .string()
      .min(8, "Password must contain at least 8 characters")
      .max(128, "Password cannot exceed 128 characters"),
  }),
});
