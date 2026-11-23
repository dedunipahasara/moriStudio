import { sendEmail as sendSmtpEmail } from "../../config/mail.js";
import type { EmailOptions, EmailResponse } from "./email.types.js";

export const sendEmail = async (
  options: EmailOptions
): Promise<EmailResponse> => {
  await sendSmtpEmail({
    to: options.to,
    subject: options.subject,
    html: options.html,
    ...(options.text !== undefined && {
      text: options.text,
    }),
  });

  return {
    success: true,
  };
};