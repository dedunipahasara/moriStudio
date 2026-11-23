import { Worker, Job } from "bullmq";
import { redisConnection } from "../config/queue.js";
import { processGeneration } from "./generation.processor.js";

interface GenerationJobData {
  generationId: string;
  userId: string;
}

const generationWorker = new Worker<GenerationJobData>(
  "generation-queue",
  async (job: Job<GenerationJobData>) => {
    console.log(
      `Processing image generation: ${job.data.generationId}`
    );

    await processGeneration(job.data);
  },
  {
    connection: redisConnection,
    concurrency: 1,
  }
);

generationWorker.on("completed", (job) => {
  console.log(`Image generation completed: ${job.id}`);
});

generationWorker.on("failed", (job, error) => {
  console.error(
    `Image generation failed: ${job?.id}`,
    error.message
  );
});

generationWorker.on("error", (error) => {
  console.error("Generation worker error:", error);
});

export default generationWorker;
