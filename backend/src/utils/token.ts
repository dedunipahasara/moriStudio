import {
  randomBytes,
  createHash,
  timingSafeEqual,
} from "node:crypto";

// Generate a secure random token
export const generateRandomToken = (
  length = 32
): string => {
  if (!Number.isInteger(length) || length < 16 || length > 128) {
    throw new Error("Token length must be between 16 and 128 bytes");
  }

  return randomBytes(length).toString("hex");
};

// Hash token using SHA-256
export const hashToken = (token: string): string => {
  return createHash("sha256")
    .update(token)
    .digest("hex");
};

// Verify token against stored hash
export const verifyToken = (
  token: string,
  hashedToken: string
): boolean => {
  const tokenHash = hashToken(token);

  const tokenBuffer = Buffer.from(tokenHash, "hex");
  const hashedBuffer = Buffer.from(hashedToken, "hex");

  if (
    tokenBuffer.length !== hashedBuffer.length ||
    hashedBuffer.length !== 32
  ) {
    return false;
  }

  return timingSafeEqual(tokenBuffer, hashedBuffer);
};
