import { sendEmail } from "./email.client.js";

import type {
  EmailOptions,
  EmailResponse,
} from "./email.types.js";

// ==========================================
// SEND GENERAL EMAIL
// ==========================================

export const sendGeneralEmail = async (
  options: EmailOptions
): Promise<EmailResponse> => {
  return await sendEmail(options);
};

// ==========================================
// SEND WELCOME EMAIL
// ==========================================

export const sendWelcomeEmail = async (
  email: string,
  name: string
): Promise<EmailResponse> => {
  return await sendEmail({
    to: email,
    subject: "Welcome to Cute3D Studio!",
    html: `
      <h2>Welcome to Cute3D Studio, ${name}!</h2>
      <p>Your account has been created successfully.</p>
      <p>Start creating images from your ideas with Cute3D Studio.</p>
    `,
    text: `Welcome to Cute3D Studio, ${name}! Your account has been created successfully.`,
  });
};

// ==========================================
// SEND EMAIL VERIFICATION
// ==========================================

export const sendVerificationEmail = async (
  email: string,
  name: string,
  verificationUrl: string
): Promise<EmailResponse> => {
  return await sendEmail({
    to: email,
    subject: "Verify your Cute3D Studio account",
    html: `
      <h2>Hello ${name},</h2>
      <p>Please verify your email address to activate your account.</p>
      <a href="${verificationUrl}">Verify Email</a>
      <p>This verification link is valid for 24 hours.</p>
    `,
    text: `Hello ${name}, verify your email using this link: ${verificationUrl}`,
  });
};

// ==========================================
// SEND PASSWORD RESET EMAIL
// ==========================================

export const sendPasswordResetEmail = async (
  email: string,
  name: string,
  resetUrl: string
): Promise<EmailResponse> => {
  return await sendEmail({
    to: email,
    subject: "Reset your Cute3D Studio password",
    html: `
      <h2>Hello ${name},</h2>
      <p>We received a request to reset your password.</p>
      <a href="${resetUrl}">Reset Password</a>
      <p>If you did not request this, you can ignore this email.</p>
    `,
    text: `Hello ${name}, reset your password using this link: ${resetUrl}`,
  });
};
