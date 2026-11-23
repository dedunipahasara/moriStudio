import { z } from "zod";

// The currently configured Stable Diffusion backend is validated for 512x512.
const imageDimension = z.literal(512);

export const generationStyles = [
  "auto",
  "photorealistic",
  "3d_cartoon",
  "anime",
  "digital_art",
  "product_photo",
] as const;

export const createGenerationSchema = z.object({
  body: z.object({
    prompt: z
      .string()
      .trim()
      .min(3, "Prompt must contain at least 3 characters")
      .max(1000, "Prompt cannot exceed 1000 characters"),
    style: z
      .enum(generationStyles)
      .optional()
      .default("auto"),
    width: imageDimension.optional().default(512),
    height: imageDimension.optional().default(512),
    seed: z
      .number()
      .int()
      .min(0)
      .max(2147483647)
      .optional(),
  }).strict(),
});

export const generationListSchema = z.object({
  query: z.object({
    page: z.coerce.number().int().min(1).optional(),
    limit: z.coerce.number().int().min(1).max(50).optional(),
  }),
});

export const generationIdSchema = z.object({
  params: z.object({
    id: z.string().uuid("Invalid generation ID"),
  }),
});
