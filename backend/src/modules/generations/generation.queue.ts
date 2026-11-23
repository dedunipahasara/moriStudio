import { generationQueue } from "../../config/queue.js";

interface GenerationJobData { generationId: string; userId: string; }

export async function addGenerationJob(data: GenerationJobData): Promise<void> {
  await generationQueue.add("generate-image", data, { jobId: data.generationId });
}
