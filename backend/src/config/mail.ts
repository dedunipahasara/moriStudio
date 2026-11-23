import nodemailer from "nodemailer";
import type { Transporter } from "nodemailer";

import { env } from "./env.js";

interface SendEmailInput {
  to: string;
  subject: string;
  html: string;
  text?: string;
}

let transporter: Transporter | null = null;

// Create SMTP transporter
const getTransporter = (): Transporter => {
  if (transporter) {
    return transporter;
  }

  if (
    !env.SMTP_HOST ||
    !env.SMTP_USER ||
    !env.SMTP_PASSWORD
  ) {
    throw new Error("SMTP configuration is incomplete");
  }

  transporter = nodemailer.createTransport({
    host: env.SMTP_HOST,
    port: env.SMTP_PORT,
    secure: env.SMTP_PORT === 465,
    auth: {
      user: env.SMTP_USER,
      pass: env.SMTP_PASSWORD,
    },
  });

  return transporter;
};

// Send email
export const sendEmail = async (
  data: SendEmailInput
): Promise<void> => {
  const mailer = getTransporter();

  await mailer.sendMail({
    from:
      env.SMTP_FROM ||
      `Cute3D Studio <${env.SMTP_USER}>`,
    to: data.to,
    subject: data.subject,
    html: data.html,
    text: data.text,
  });
};

// Verify SMTP connection
export const verifyMailConnection = async (): Promise<boolean> => {
  try {
    const mailer = getTransporter();

    await mailer.verify();

    return true;
  } catch (error) {
    console.error("SMTP connection failed:", error);

    return false;
  }
};
