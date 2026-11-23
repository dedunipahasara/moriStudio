
import { createHash, randomBytes } from "node:crypto";

import { prisma } from "../../config/prisma.js";
import { sendEmail } from "../../config/mail.js";
import { env } from "../../config/env.js";
import { AppError } from "../../utils/app-error.js";
import {
  hashPassword,
  verifyPassword,
} from "../../utils/password.js";

import type {
  ForgotPasswordInput,
  ResetPasswordInput,
  ChangePasswordInput,
} from "./password.types.js";

// ==========================================
// TOKEN UTILITIES
// ==========================================

const hashToken = (token: string): string => {
  return createHash("sha256").update(token).digest("hex");
};

const generateResetToken = (): string => {
  return randomBytes(32).toString("hex");
};

// ==========================================
// FORGOT PASSWORD
// ==========================================

export const forgotPassword = async (
  data: ForgotPasswordInput
): Promise<void> => {
  const email = data.email.trim().toLowerCase();

  const user = await prisma.user.findUnique({
    where: { email },
  });

  // Do not reveal whether an email address is registered.
  if (!user) {
    return;
  }

  // Generate a secure random token.
  const rawToken = generateResetToken();

  // Store only the hashed token in the database.
  const tokenHash = hashToken(rawToken);

  // Token expires after 15 minutes.
  const expiresAt = new Date(Date.now() + 15 * 60 * 1000);

  // Invalidate previous unused reset tokens and create a new one.
  await prisma.$transaction(async (tx) => {
    await tx.passwordResetToken.updateMany({
      where: {
        userId: user.id,
        usedAt: null,
      },
      data: {
        usedAt: new Date(),
      },
    });

    await tx.passwordResetToken.create({
      data: {
        userId: user.id,
        tokenHash,
        expiresAt,
      },
    });
  });

  // Create frontend password reset URL.
  const resetUrl = new URL(
    "/reset-password",
    env.FRONTEND_URL
  );

  resetUrl.searchParams.set("token", rawToken);

  // Send password reset email.
  try {
    await sendEmail({
      to: user.email,
      subject: "Reset your Cute3D Studio password",

      text: `
We received a request to reset your Cute3D Studio password.

Use the following link to reset your password:

${resetUrl.toString()}

This link expires in 15 minutes.

If you did not request this, you can ignore this email.
      `.trim(),

      html: `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto;">
          <h2>Reset Your Password</h2>

          <p>
            We received a request to reset your Cute3D Studio password.
          </p>

          <p>
            Click the button below to create a new password.
          </p>

          <a
            href="${resetUrl.toString()}"
            style="
              display: inline-block;
              padding: 12px 24px;
              background-color: #16a34a;
              color: #ffffff;
              text-decoration: none;
              border-radius: 6px;
            "
          >
            Reset Password
          </a>

          <p>
            This link expires in 15 minutes.
          </p>

          <p>
            If you did not request this password reset,
            you can safely ignore this email.
          </p>

          <p>Regards,<br />Cute3D Studio Team</p>
        </div>
      `,
    });
  } catch (error) {
    // Log the email delivery failure without exposing internal details.
    console.error("Password reset email delivery failed:", error);

    throw new AppError(
      "Unable to send password reset email. Please try again later.",
      503
    );
  }
};

// ==========================================
// RESET PASSWORD
// ==========================================

export const resetPassword = async (
  data: ResetPasswordInput
): Promise<void> => {
  // Hash the token received from the frontend.
  const tokenHash = hashToken(data.token);

  // Find the matching reset token.
  const resetToken = await prisma.passwordResetToken.findUnique({
    where: {
      tokenHash,
    },
  });

  // Validate token existence, usage and expiration.
  if (
    !resetToken ||
    resetToken.usedAt !== null ||
    resetToken.expiresAt <= new Date()
  ) {
    throw new AppError(
      "Invalid or expired password reset token",
      400
    );
  }

  // Hash the new password.
  const passwordHash = await hashPassword(data.newPassword);

  // Atomically mark the token as used and update the password.
  await prisma.$transaction(async (tx) => {
    const result = await tx.passwordResetToken.updateMany({
      where: {
        id: resetToken.id,
        usedAt: null,
        expiresAt: {
          gt: new Date(),
        },
      },
      data: {
        usedAt: new Date(),
      },
    });

    // Prevent reuse if another request already consumed the token.
    if (result.count !== 1) {
      throw new AppError(
        "Invalid or expired password reset token",
        400
      );
    }

    await tx.user.update({
      where: {
        id: resetToken.userId,
      },
      data: {
        passwordHash,
      },
    });

    // Invalidate other unused reset tokens belonging to this user.
    await tx.passwordResetToken.updateMany({
      where: {
        userId: resetToken.userId,
        usedAt: null,
      },
      data: {
        usedAt: new Date(),
      },
    });
  });
};

// ==========================================
// CHANGE PASSWORD
// ==========================================

export const changePassword = async (
  userId: string,
  data: ChangePasswordInput
): Promise<void> => {
  // Find authenticated user.
  const user = await prisma.user.findUnique({
    where: {
      id: userId,
    },
  });

  if (!user) {
    throw new AppError("User not found", 404);
  }

  // Verify current password.
  const isPasswordValid = await verifyPassword(
    data.currentPassword,
    user.passwordHash
  );

  if (!isPasswordValid) {
    throw new AppError(
      "Current password is incorrect",
      400
    );
  }

  // Prevent using the same password again.
  if (data.currentPassword === data.newPassword) {
    throw new AppError(
      "New password must be different from current password",
      400
    );
  }

  // Hash the new password.
  const passwordHash = await hashPassword(data.newPassword);

  // Update password in database.
  await prisma.user.update({
    where: {
      id: userId,
    },
    data: {
      passwordHash,
    },
  });

  // Invalidate existing unused password reset tokens.
  await prisma.passwordResetToken.updateMany({
    where: {
      userId,
      usedAt: null,
    },
    data: {
      usedAt: new Date(),
    },
  });
};
