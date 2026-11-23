import "dotenv/config";

import app from "./app.js";
import { env } from "./config/env.js";
import { prisma } from "./config/prisma.js";
import { redisConnection, closeQueue } from "./config/queue.js";
import { verifyMailConnection } from "./config/mail.js";
import { initializeStorage } from "./config/storage.js";
import "./workers/generation.worker.js";

const startServer = async (): Promise<void> => {
  try {
    // 1. Prepare private local storage
    await initializeStorage();
    console.log("Image storage initialized");

    // 2. Connect to PostgreSQL
    await prisma.$connect();
    console.log("PostgreSQL connected successfully");

    // 3. Check Redis connection
    await redisConnection.ping();
    console.log("Redis connected successfully");

    // 4. Verify SMTP connection
    const emailConnected = await verifyMailConnection();

    if (emailConnected) {
      console.log("SMTP connection verified successfully");
    } else {
      console.warn("SMTP connection verification failed");
    }

    // 5. Start Express server
    const server = app.listen(env.PORT, () => {
      console.log(`Cute3D Studio API running on port ${env.PORT}`);
      console.log(`Environment: ${env.NODE_ENV}`);
      console.log(`Health URL: http://localhost:${env.PORT}/health`);
    });

    // 6. Graceful shutdown
    const shutdown = async (signal: string): Promise<void> => {
      console.log(`${signal} received. Shutting down server...`);

      server.close(async () => {
        try {
          await closeQueue();
          await prisma.$disconnect();

          console.log("Server shutdown completed");
          process.exit(0);
        } catch (error) {
          console.error("Error during shutdown:", error);
          process.exit(1);
        }
      });
    };

    process.on("SIGINT", () => {
      void shutdown("SIGINT");
    });

    process.on("SIGTERM", () => {
      void shutdown("SIGTERM");
    });
  } catch (error) {
    console.error("Failed to start Cute3D Studio API:", error);

    await prisma.$disconnect().catch(() => undefined);
    await closeQueue().catch(() => undefined);

    process.exit(1);
  }
};

void startServer();
