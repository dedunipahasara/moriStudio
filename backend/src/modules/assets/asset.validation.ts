import { z } from "zod";
export const assetIdSchema = z.object({ params: z.object({ id: z.string().uuid("Invalid asset ID") }) });
export const assetModelIdSchema = z.object({ params: z.object({ generationId: z.string().uuid("Invalid generation ID") }) });
export const assetListSchema = z.object({ query: z.object({ page: z.coerce.number().int().min(1).optional(), limit: z.coerce.number().int().min(1).max(50).optional() }) });
