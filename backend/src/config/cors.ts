import cors from "cors";
import type { CorsOptions } from "cors";
import { env } from "./env.js";

const corsOptions: CorsOptions = {
  origin: (origin, callback) => {
    // Allow requests without an Origin header (e.g. Postman)
    if (!origin) {
      return callback(null, true);
    }

    if (origin === env.FRONTEND_URL) {
      return callback(null, true);
    }

    return callback(new Error("Not allowed by CORS"));
  },

  methods: ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],

  allowedHeaders: ["Content-Type", "Authorization"],

  credentials: true,
};

export const corsMiddleware = cors(corsOptions);
