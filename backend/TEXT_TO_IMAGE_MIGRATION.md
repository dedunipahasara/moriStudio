# Text-to-Image backend conversion

This archive adapts the supplied Express + Prisma backend from 3D model generation to internal text-to-image generation.

## Preserved modules

Authentication, users, password reset, email verification, SMTP integration, PostgreSQL, Redis/BullMQ, upload authentication and user ownership are retained.

## Updated modules

- `Generation` stores prompt, style, width, height, seed and status.
- `GeneratedModel` is renamed to `GeneratedImage`.
- `ModelAsset` is renamed to `GeneratedImageAsset`; asset types are `IMAGE`, `THUMBNAIL`, and `OTHER`.
- Model API module is now `src/modules/images` and is mounted at `/api/images`.
- Assets are mounted at `/api/assets`; list assets for a generation with `GET /api/assets/generation/:generationId`.
- The worker calls the local AI Engine and persists returned image bytes to private backend storage.
- Uploaded reference images are now persisted in `UploadedAsset` with the authenticated user's ID.

## AI Engine response contract expected by the backend

`POST {AI_ENGINE_URL}/api/generations` receives JSON:

```json
{
  "generationId": "uuid",
  "userId": "uuid",
  "prompt": "A small red wooden house",
  "style": "watercolor",
  "width": 512,
  "height": 512,
  "seed": 123
}
```

It must return JSON:

```json
{
  "success": true,
  "imageBase64": "<base64-encoded PNG/JPEG/WEBP bytes>",
  "mimeType": "image/png",
  "seed": 123
}
```

`imageBase64` is required on success. Supported MIME types are PNG, JPEG and WEBP, and the backend enforces a 15 MiB decoded image limit. The backend stores the image and creates the corresponding Prisma records. The AI Engine must not return a filesystem path from its own private container because that path may not be accessible to the backend.

## Main API routes

- `POST /api/auth/register`, `POST /api/auth/login`
- `POST /api/password/forgot`, `POST /api/password/reset`, `POST /api/password/change`
- `POST /api/email-verification/verify`, `POST /api/email-verification/resend`
- `GET /api/users/me`, `PATCH /api/users/me`
- `POST /api/uploads/image` (multipart field name: `image`; authentication required)
- `POST /api/generations` (authentication required; prompt, optional style, width, height, seed)
- `GET /api/generations`, `GET /api/generations/:id`
- `GET /api/images`, `GET /api/images/:id`, `PATCH /api/images/:id`
- `GET /api/assets/generation/:generationId`, `GET /api/assets/:id`, `GET /api/assets/:id/file`, `DELETE /api/assets/:id`

All image and generation history endpoints require a valid bearer token.

## Database migration

A new migration is provided at `prisma/migrations/20261120120000_text_to_image/migration.sql`. It renames the existing generated-model tables and preserves existing rows. Old GLB/GLTF asset rows are retained as `OTHER`; old preview image assets become `IMAGE`.

Before applying the migration, back up the database. Run from the backend project directory:

```bash
pnpm exec prisma validate
pnpm exec prisma migrate deploy
pnpm exec prisma generate
```

For local development with Prisma migrate dev, use:

```bash
pnpm exec prisma migrate dev
pnpm exec prisma generate
```

## Important archive limitation

The uploaded ZIP did not contain `package.json`, lockfile, `tsconfig.json`, `.env`, or a complete root project manifest. Those files were not invented or replaced in this output. Merge these changes into the original backend directory, retaining its real dependency manifests and environment configuration. Ensure the backend dependencies include the versions already used by the project (Express, Prisma, BullMQ, ioredis, multer, zod, etc.).

The ZIP is a source conversion, not a claim that it has been compiled or run against your local PostgreSQL/Redis/AI Engine. The AI Engine itself still needs to implement the response contract above.
