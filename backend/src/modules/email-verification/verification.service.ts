import { createHash, randomInt } from "node:crypto";

import { prisma } from "../../config/prisma.js";
import { sendEmail } from "../../config/mail.js";
import { AppError } from "../../utils/app-error.js";

import type {
  VerifyEmailInput,
  ResendVerificationInput,
} from "./verification.types.js";

// ==========================================
// TOKEN UTILITIES
// ==========================================

const hashToken = (token: string): string => {
  return createHash("sha256").update(token).digest("hex");
};

const generateVerificationToken = (): string => {
  return randomInt(100000, 1000000).toString();
};

// ==========================================
// SEND VERIFICATION EMAIL
// ==========================================

export const sendVerificationEmail = async (
  userId: string,
  email: string,
  name: string
): Promise<void> => {
  const rawToken = generateVerificationToken();
  const tokenHash = hashToken(rawToken);

  const expiresAt = new Date(Date.now() + 10 * 60 * 1000);

  await prisma.$transaction(async (tx) => {
    await tx.emailVerificationToken.updateMany({
      where: {
        userId,
        usedAt: null,
      },
      data: {
        usedAt: new Date(),
      },
    });

    await tx.emailVerificationToken.create({
      data: {
        userId,
        tokenHash,
        expiresAt,
      },
    });
  });

  try {
    await sendEmail({
      to: email,
      subject: "Your Mori Studio verification code",
      text: `
Hello ${name},

Your Mori Studio email verification code is:

${rawToken}

This code expires in 10 minutes. Enter it in the verification screen to activate your account.

If you did not create this account, you can ignore this email.
      `.trim(),
      html: `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 32px; color: #33223f;">
          <h2 style="color: #4C2365;">Verify your Mori Studio account</h2>
          <p>Hello ${name},</p>
          <p>Enter this one-time code in Mori Studio to verify your email address.</p>
          <div style="display: inline-block; padding: 18px 28px; margin: 16px 0; background: #f5eef9; border-radius: 14px; color: #4C2365; font-size: 30px; font-weight: 700; letter-spacing: 9px;">${rawToken}</div>
          <p>This code expires in <strong>10 minutes</strong>.</p>
          <p>If you did not create this account, you can ignore this email.</p>
          <p>Regards,<br/>Mori Studio Team</p>
        </div>
      `,
    });
  } catch (error) {
    console.error("Verification email delivery failed:", error);

    throw new AppError(
      "Unable to send verification email. Please try again later.",
      503
    );
  }
};

// ==========================================
// VERIFY EMAIL
// ==========================================

export const verifyEmail = async (
  data: VerifyEmailInput
): Promise<void> => {
  const tokenHash = hashToken(data.token);

  const verificationToken =
    await prisma.emailVerificationToken.findUnique({
      where: {
        tokenHash,
      },
    });

  if (
    !verificationToken ||
    verificationToken.usedAt !== null ||
    verificationToken.expiresAt <= new Date()
  ) {
    throw new AppError(
      "Invalid or expired verification code",
      400
    );
  }

  await prisma.$transaction(async (tx) => {
    const result = await tx.emailVerificationToken.updateMany({
      where: {
        id: verificationToken.id,
        usedAt: null,
        expiresAt: {
          gt: new Date(),
        },
      },
      data: {
        usedAt: new Date(),
      },
    });

    if (result.count !== 1) {
      throw new AppError(
        "Invalid or expired verification code",
        400
      );
    }

    await tx.user.update({
      where: {
        id: verificationToken.userId,
        emailVerifiedAt: null,
      },
      data: {
        emailVerifiedAt: new Date(),
      },
    });

    await tx.emailVerificationToken.updateMany({
      where: {
        userId: verificationToken.userId,
        usedAt: null,
      },
      data: {
        usedAt: new Date(),
      },
    });
  });
};

// ==========================================
// RESEND VERIFICATION EMAIL
// ==========================================

export const resendVerificationEmail = async (
  data: ResendVerificationInput
): Promise<void> => {
  const email = data.email.trim().toLowerCase();

  const user = await prisma.user.findUnique({
    where: {
      email,
    },
  });

  // Do not reveal whether the account exists.
  if (!user || user.emailVerifiedAt !== null) {
    return;
  }

  await sendVerificationEmail(
    user.id,
    user.email,
    user.name
  );
};
