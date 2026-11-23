import { z } from "zod";

export const imageIdSchema = z.object({ params: z.object({ id: z.string().uuid("Invalid image ID") }) });
export const imageListSchema = z.object({ query: z.object({ page: z.coerce.number().int().min(1).optional(), limit: z.coerce.number().int().min(1).max(50).optional() }) });
export const updateImageSchema = z.object({
  params: z.object({ id: z.string().uuid("Invalid image ID") }),
  body: z.object({
    name: z.string().trim().min(2).max(150).optional(),
    description: z.string().trim().max(2000).nullable().optional(),
  }).strict().refine((data) => data.name !== undefined || data.description !== undefined, "At least one field must be provided"),
});
