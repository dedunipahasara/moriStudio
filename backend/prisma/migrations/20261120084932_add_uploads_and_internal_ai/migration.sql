/*
  Warnings:

  - You are about to drop the column `providerTaskId` on the `Generation` table. All the data in the column will be lost.

*/
-- DropIndex
DROP INDEX "Generation_providerTaskId_key";

-- AlterTable
ALTER TABLE "Generation" DROP COLUMN "providerTaskId",
ALTER COLUMN "provider" SET DEFAULT 'internal';

-- CreateTable
CREATE TABLE "UploadedAsset" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "originalName" TEXT NOT NULL,
    "filename" TEXT NOT NULL,
    "storagePath" TEXT NOT NULL,
    "mimeType" TEXT NOT NULL,
    "fileSize" BIGINT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "UploadedAsset_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "UploadedAsset_filename_key" ON "UploadedAsset"("filename");

-- CreateIndex
CREATE INDEX "UploadedAsset_userId_idx" ON "UploadedAsset"("userId");

-- CreateIndex
CREATE INDEX "UploadedAsset_createdAt_idx" ON "UploadedAsset"("createdAt");

-- CreateIndex
CREATE INDEX "GeneratedModel_createdAt_idx" ON "GeneratedModel"("createdAt");

-- CreateIndex
CREATE INDEX "ModelAsset_type_idx" ON "ModelAsset"("type");

-- CreateIndex
CREATE INDEX "User_email_idx" ON "User"("email");

-- AddForeignKey
ALTER TABLE "UploadedAsset" ADD CONSTRAINT "UploadedAsset_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;
