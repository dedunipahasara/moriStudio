import type { Express } from "express";
import path from "node:path";
import { unlink } from "node:fs/promises";
import { prisma } from "../../config/prisma.js";
import { AppError } from "../../utils/app-error.js";

export const saveUploadedFile = async (userId: string, file: Express.Multer.File) => {
  if (!file) throw new AppError("Please select an image to upload.", 400);
  const storagePath = path.posix.join("uploads", "images", file.filename);
  try {
    const asset = await prisma.uploadedAsset.create({
      data: { userId, originalName: file.originalname, filename: file.filename, storagePath, mimeType: file.mimetype, fileSize: BigInt(file.size) },
      select: { id: true, originalName: true, filename: true, storagePath: true, mimeType: true, fileSize: true, createdAt: true },
    });
    return { ...asset, fileSize: asset.fileSize.toString() };
  } catch (error) {
    await unlink(file.path).catch(() => undefined);
    throw error;
  }
};
