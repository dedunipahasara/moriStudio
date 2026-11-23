import { prisma } from "../../config/prisma.js";
import { AppError } from "../../utils/app-error.js";
import { addGenerationJob } from "./generation.queue.js";
import type {
  CreateGenerationInput,
  GenerationQuery,
} from "./generation.types.js";

const generationSelect = {
  id: true,
  prompt: true,
  style: true,
  width: true,
  height: true,
  seed: true,
  status: true,
  provider: true,
  errorMessage: true,
  createdAt: true,
  updatedAt: true,
} as const;

const formatAsset = <
  T extends {
    id: string;
    fileSize: bigint | null;
  }
>(asset: T) => ({
  ...asset,
  downloadUrl: `/api/assets/${asset.id}/file`,
  fileSize: asset.fileSize?.toString() ?? null,
});

const formatImage = <
  T extends {
    assets: Array<{
      id: string;
      fileSize: bigint | null;
    }>;
  }
>(image: T) => ({
  ...image,
  assets: image.assets.map(formatAsset),
});

/**
 * Creates a generation record and enqueues its background job.
 *
 * The generation is marked FAILED if the queue cannot accept the job.
 */
export const createGeneration = async (
  userId: string,
  data: CreateGenerationInput,
) => {
  const prompt = data.prompt.trim();

  if (!prompt) {
    throw new AppError("Prompt cannot be empty.", 400);
  }

  const generation = await prisma.generation.create({
    data: {
      userId,
      prompt,
      style: data.style?.trim() || "auto",
      width: data.width ?? 512,
      height: data.height ?? 512,
      seed: data.seed ?? null,
      status: "PENDING",
      provider: "internal",
    },
    select: generationSelect,
  });

  try {
    await addGenerationJob({
      generationId: generation.id,
      userId,
    });
  } catch (error) {
    await prisma.generation.updateMany({
      where: {
        id: generation.id,
        userId,
        status: "PENDING",
      },
      data: {
        status: "FAILED",
        errorMessage: "Failed to add image generation to the queue.",
      },
    });

    throw new AppError(
      "Unable to start image generation. Please try again.",
      503,
    );
  }

  return generation;
};

/**
 * Returns the authenticated user's generation history.
 * BigInt file sizes are converted to strings for JSON serialization.
 */
export const getUserGenerations = async (
  userId: string,
  query: GenerationQuery,
) => {
  const page = Math.max(1, query.page);
  const limit = Math.min(50, Math.max(1, query.limit));
  const where = { userId };

  const [generations, total] = await prisma.$transaction([
    prisma.generation.findMany({
      where,
      select: {
        ...generationSelect,
        image: {
          select: {
            id: true,
            name: true,
            description: true,
            assets: {
              select: {
                id: true,
                type: true,
                fileUrl: true,
                mimeType: true,
                fileSize: true,
              },
            },
          },
        },
      },
      orderBy: { createdAt: "desc" },
      skip: (page - 1) * limit,
      take: limit,
    }),
    prisma.generation.count({ where }),
  ]);

  return {
    generations: generations.map((generation) => ({
      ...generation,
      image: generation.image
        ? formatImage(generation.image)
        : null,
    })),
    pagination: {
      page,
      limit,
      total,
      totalPages: Math.ceil(total / limit),
    },
  };
};

/**
 * Returns one generation belonging to the authenticated user.
 */
export const getGenerationById = async (
  userId: string,
  generationId: string,
) => {
  const generation = await prisma.generation.findFirst({
    where: {
      id: generationId,
      userId,
    },
    select: {
      ...generationSelect,
      image: {
        select: {
          id: true,
          name: true,
          description: true,
          createdAt: true,
          updatedAt: true,
          assets: {
            select: {
              id: true,
              type: true,
              fileUrl: true,
              mimeType: true,
              fileSize: true,
              createdAt: true,
            },
          },
        },
      },
    },
  });

  if (!generation) {
    throw new AppError("Generation not found.", 404);
  }

  return {
    ...generation,
    image: generation.image
      ? formatImage(generation.image)
      : null,
  };
};
