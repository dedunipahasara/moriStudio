
import jwt, { type SignOptions } from "jsonwebtoken";

import { prisma } from "../../config/prisma.js";
import { env } from "../../config/env.js";
import { AppError } from "../../utils/app-error.js";
import { sendVerificationEmail } from "../email-verification/verification.service.js";

import {
  hashPassword,
  verifyPassword,
} from "../../utils/password.js";

import type {
  RegisterInput,
  LoginInput,
  AuthResult,
} from "./auth.types.js";

// ==========================================
// REGISTER USER
// ==========================================

export const registerUser = async (data: RegisterInput) => {
  const email = data.email.trim().toLowerCase();

  // Check existing email
  const existingUser = await prisma.user.findUnique({
    where: {
      email,
    },
  });

  if (existingUser) {
    throw new AppError("Email is already registered", 409);
  }

  // Hash password using Argon2id
  const passwordHash = await hashPassword(data.password);

  try {
    // Create new user
    const user = await prisma.user.create({
      data: {
        name: data.name.trim(),
        email,
        passwordHash,
      },
      select: {
        id: true,
        name: true,
        email: true,
        createdAt: true,
      },
    });

    // Send a one-time email verification code after account creation.
    await sendVerificationEmail(user.id, user.email, user.name);
    return user;
  } catch (error) {
    // Handle duplicate email error
    if (
      typeof error === "object" &&
      error !== null &&
      "code" in error &&
      error.code === "P2002"
    ) {
      throw new AppError("Email is already registered", 409);
    }

    throw error;
  }
};

// ==========================================
// LOGIN USER
// ==========================================

export const loginUser = async (
  data: LoginInput
): Promise<AuthResult> => {
  const email = data.email.trim().toLowerCase();

  // Find user
  const user = await prisma.user.findUnique({
    where: {
      email,
    },
  });

  if (!user) {
    throw new AppError("Invalid email or password", 401);
  }

  // Verify password
  const isPasswordValid = await verifyPassword(
    data.password,
    user.passwordHash
  );

  if (!isPasswordValid) {
    throw new AppError("Invalid email or password", 401);
  }

  // Require email verification before allowing account access.
  if (!user.emailVerifiedAt) {
    throw new AppError(
      "Please verify your email address before logging in.",
      403
    );
  }

  // JWT options
  const jwtOptions: SignOptions = {
    expiresIn: env.JWT_EXPIRES_IN as NonNullable<
      SignOptions["expiresIn"]
    >,
  };

  // Generate JWT access token
  const accessToken = jwt.sign(
    {
      userId: user.id,
      email: user.email,
    },
    env.JWT_SECRET,
    jwtOptions
  );

  // Return user details and token
  return {
    user: {
      id: user.id,
      name: user.name,
      email: user.email,
    },
    accessToken,
  };
};
