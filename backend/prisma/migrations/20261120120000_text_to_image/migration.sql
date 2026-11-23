-- Convert the existing 3D-oriented records to image-generation terminology.
-- Existing GLB/GLTF assets are retained and reclassified as OTHER; preview images become IMAGE.

ALTER TABLE "Generation" ADD COLUMN "width" INTEGER NOT NULL DEFAULT 512;
ALTER TABLE "Generation" ADD COLUMN "height" INTEGER NOT NULL DEFAULT 512;
ALTER TABLE "Generation" ADD COLUMN "seed" INTEGER;

ALTER TABLE "GeneratedModel" RENAME TO "GeneratedImage";
ALTER TABLE "ModelAsset" RENAME TO "GeneratedImageAsset";
ALTER TABLE "GeneratedImageAsset" RENAME COLUMN "modelId" TO "imageId";

ALTER TABLE "GeneratedImageAsset" DROP CONSTRAINT IF EXISTS "ModelAsset_modelId_fkey";
ALTER TABLE "GeneratedImageAsset" ADD CONSTRAINT "GeneratedImageAsset_imageId_fkey"
  FOREIGN KEY ("imageId") REFERENCES "GeneratedImage"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "GeneratedImage" RENAME CONSTRAINT "GeneratedModel_pkey" TO "GeneratedImage_pkey";
ALTER INDEX IF EXISTS "GeneratedModel_generationId_key" RENAME TO "GeneratedImage_generationId_key";
ALTER TABLE "GeneratedImage" RENAME CONSTRAINT "GeneratedModel_generationId_fkey" TO "GeneratedImage_generationId_fkey";
ALTER TABLE "GeneratedImageAsset" RENAME CONSTRAINT "ModelAsset_pkey" TO "GeneratedImageAsset_pkey";
ALTER INDEX IF EXISTS "GeneratedModel_createdAt_idx" RENAME TO "GeneratedImage_createdAt_idx";
ALTER INDEX IF EXISTS "ModelAsset_modelId_idx" RENAME TO "GeneratedImageAsset_imageId_idx";
ALTER INDEX IF EXISTS "ModelAsset_type_idx" RENAME TO "GeneratedImageAsset_type_idx";

ALTER TYPE "AssetType" RENAME TO "AssetType_old";
CREATE TYPE "AssetType" AS ENUM ('IMAGE', 'THUMBNAIL', 'OTHER');
ALTER TABLE "GeneratedImageAsset" ALTER COLUMN "type" TYPE "AssetType"
  USING (CASE
    WHEN "type"::text = 'PREVIEW_IMAGE' THEN 'IMAGE'
    WHEN "type"::text IN ('GLB', 'GLTF') THEN 'OTHER'
    ELSE 'OTHER'
  END)::"AssetType";
DROP TYPE "AssetType_old";
