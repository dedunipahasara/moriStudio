import dotenv from "dotenv";
import { z } from "zod";

// Load environment variables
dotenv.config();

// Define environment variable schema
const envSchema = z.object({
  NODE_ENV: z
    .enum(["development", "production", "test"])
    .default("development"),

  PORT: z.coerce.number().int().positive().default(5000),

  DATABASE_URL: z.string().min(1, "DATABASE_URL is required"),

  JWT_SECRET: z.string().min(32, "JWT_SECRET must be at least 32 characters"),

  JWT_EXPIRES_IN: z.string().default("7d"),

  FRONTEND_URL: z.string().url().default("http://localhost:5173"),

  // Email configuration
  SMTP_HOST: z.string().optional(),
  SMTP_PORT: z.coerce.number().int().positive().default(587),
  SMTP_USER: z.string().optional(),
  SMTP_PASSWORD: z.string().optional(),
  SMTP_FROM: z.string().optional(),

  // Local AI Engine configuration
  AI_ENGINE_URL: z.string().url().default("http://127.0.0.1:8000"),

  // Redis configuration
  REDIS_HOST: z.string().default("127.0.0.1"),
  REDIS_PORT: z.coerce.number().int().positive().default(6379),

  // File storage
  STORAGE_PATH: z.string().default("./storage"),
});

// Validate environment variables
const parsedEnv = envSchema.safeParse(process.env);

if (!parsedEnv.success) {
  console.error(
    "Invalid environment variables:",
    z.treeifyError(parsedEnv.error)
  );

  process.exit(1);
}

// Export validated environment variables
export const env = parsedEnv.data;
