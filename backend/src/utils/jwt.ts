import jwt, {
  type JwtPayload,
  type SignOptions,
} from "jsonwebtoken";

import { env } from "../config/env.js";

export interface AccessTokenPayload extends JwtPayload {
  userId: string;
  email: string;
}

// Generate JWT Access Token
export const generateAccessToken = (
  payload: AccessTokenPayload
): string => {
  const expiresIn = (
    env.JWT_EXPIRES_IN ?? "15m"
  ) as NonNullable<SignOptions["expiresIn"]>;

  return jwt.sign(
    {
      userId: payload.userId,
      email: payload.email,
    },
    env.JWT_SECRET,
    {
      expiresIn,
    }
  );
};

// Verify JWT Access Token
export const verifyAccessToken = (
  token: string
): AccessTokenPayload => {
  const decoded = jwt.verify(token, env.JWT_SECRET);

  if (
    typeof decoded === "string" ||
    typeof decoded.userId !== "string" ||
    typeof decoded.email !== "string"
  ) {
    throw new Error("Invalid access token payload");
  }

  return decoded as AccessTokenPayload;
};

// Decode JWT without verifying signature
export const decodeAccessToken = (
  token: string
): JwtPayload | null => {
  const decoded = jwt.decode(token);

  if (!decoded || typeof decoded === "string") {
    return null;
  }

  return decoded;
};
