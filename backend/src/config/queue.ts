
import { Redis } from "ioredis";
import { Queue } from "bullmq";
import { env } from "./env.js";

// Redis connection
export const redisConnection = new Redis({
  host: env.REDIS_HOST,
  port: env.REDIS_PORT,
  maxRetriesPerRequest: null,
});

// Generation queue
export const generationQueue = new Queue("generation-queue", {
  connection: redisConnection,
  defaultJobOptions: {
    attempts: 3,
    backoff: {
      type: "exponential",
      delay: 5000,
    },
    removeOnComplete: {
      age: 24 * 60 * 60,
      count: 1000,
    },
    removeOnFail: false,
  },
});

// Redis connection events
redisConnection.on("connect", () => {
  console.log("Redis connected successfully");
});

redisConnection.on("error", (error) => {
  console.error("Redis connection error:", error);
});

export async function closeQueue(): Promise<void> {
  await generationQueue.close();
  await redisConnection.quit();
}
