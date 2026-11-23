# Cute3D Backend Review Notes

## Updated files

- `src/modules/generations/generation.service.ts`
  - Centralized generation selection and JSON-safe asset formatting.
  - Fixed BigInt `fileSize` serialization for both list and detail responses.
  - Added defensive pagination bounds and prompt validation.
  - Uses `auto` when no style is supplied.
- `src/modules/generations/generation.validation.ts`
  - Aligns prompt length with the AI Engine's 1000-character limit.
  - Restricts dimensions to 512x512 to match the currently configured AI Engine backend.
  - Validates the six style preset keys supported by the AI Engine.
- `src/workers/generation.processor.ts`
  - Sends the FastAPI request fields expected by the AI Engine (without unsupported `generationId` and `userId` fields).
  - Defaults a missing style to `auto`.
  - Accepts the AI Engine's snake_case response (`image_base64`, `mime_type`) and compatible camelCase aliases.
  - Validates Base64, image signatures, MIME types and output size.
  - Handles non-2xx AI Engine responses with useful error messages.
  - Makes completed-job retries idempotent and avoids duplicate generated-image records.

## Integration assumptions to verify

1. The AI Engine is reachable at `AI_ENGINE_URL` and exposes `POST /api/generations`.
2. Its request schema accepts `prompt`, `style`, `width`, `height`, `seed`, and `negative_prompt`.
3. Its response contains `image_base64` and optionally `mime_type`, `seed`.
4. The active AI Engine currently supports 512x512 only and the six style keys in `generation.validation.ts`.

## Validation limitation

The supplied ZIP contains the source tree and Prisma migrations/schema, but does not contain `package.json`, lockfile, or `tsconfig.json`. Therefore a full TypeScript build, Prisma generation, and runtime integration test cannot be performed from this archive alone. Run the project's normal install/build/test commands in the original backend repository after merging these changes.
