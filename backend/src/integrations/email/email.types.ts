export interface EmailOptions {
  to: string;
  subject: string;
  html: string;
  text?: string;
}

export interface EmailTemplateData {
  name: string;
  [key: string]: string;
}

export interface EmailResponse {
  success: boolean;
  messageId?: string;
}
