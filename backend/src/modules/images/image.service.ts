import { prisma } from "../../config/prisma.js";
import { AppError } from "../../utils/app-error.js";

export interface ImageListQuery { page: number; limit: number; }
export interface UpdateImageInput { name?: string; description?: string | null; }

const formatImage = <T extends { assets: Array<{ fileSize: bigint | null }> }>(image: T) => ({
  ...image,
  assets: image.assets.map((asset) => ({ ...asset, downloadUrl: `/api/assets/${asset.id}/file`, fileSize: asset.fileSize?.toString() ?? null })),
});

export const getUserImages = async (userId: string, query: ImageListQuery) => {
  const { page, limit } = query;
  const where = { generation: { userId } };
  const [images, total] = await prisma.$transaction([
    prisma.generatedImage.findMany({
      where,
      select: {
        id: true, generationId: true, name: true, description: true, createdAt: true, updatedAt: true,
        generation: { select: { prompt: true, style: true, width: true, height: true, seed: true, status: true } },
        assets: { select: { id: true, type: true, fileUrl: true, mimeType: true, fileSize: true, createdAt: true } },
      },
      orderBy: { createdAt: "desc" }, skip: (page - 1) * limit, take: limit,
    }),
    prisma.generatedImage.count({ where }),
  ]);
  return { images: images.map(formatImage), pagination: { page, limit, total, totalPages: Math.ceil(total / limit) } };
};

export const getImageById = async (userId: string, imageId: string) => {
  const image = await prisma.generatedImage.findFirst({
    where: { id: imageId, generation: { userId } },
    select: {
      id: true, generationId: true, name: true, description: true, createdAt: true, updatedAt: true,
      generation: { select: { id: true, prompt: true, style: true, width: true, height: true, seed: true, status: true, createdAt: true } },
      assets: { select: { id: true, type: true, fileUrl: true, mimeType: true, fileSize: true, createdAt: true } },
    },
  });
  if (!image) throw new AppError("Image not found", 404);
  return formatImage(image);
};

export const updateImage = async (userId: string, imageId: string, data: UpdateImageInput) => {
  const existing = await prisma.generatedImage.findFirst({ where: { id: imageId, generation: { userId } }, select: { id: true } });
  if (!existing) throw new AppError("Image not found", 404);
  const image = await prisma.generatedImage.update({
    where: { id: imageId },
    data: {
      ...(data.name !== undefined ? { name: data.name.trim() } : {}),
      ...(data.description !== undefined ? { description: data.description?.trim() || null } : {}),
    },
    select: { id: true, generationId: true, name: true, description: true, createdAt: true, updatedAt: true,
      assets: { select: { id: true, type: true, fileUrl: true, mimeType: true, fileSize: true, createdAt: true } } },
  });
  return formatImage(image);
};
