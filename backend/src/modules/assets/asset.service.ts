import { prisma } from "../../config/prisma.js";
import { AppError } from "../../utils/app-error.js";
import { deleteFile } from "../../config/storage.js";

export interface AssetListQuery { page: number; limit: number; }
const formatAsset = <T extends { id: string; fileSize: bigint | null }>(asset: T) => ({ ...asset, downloadUrl: `/api/assets/${asset.id}/file`, fileSize: asset.fileSize?.toString() ?? null });

export const getGenerationAssets = async (userId: string, generationId: string, query: AssetListQuery) => {
  const generation = await prisma.generation.findFirst({ where: { id: generationId, userId }, select: { image: { select: { id: true } } } });
  if (!generation?.image) throw new AppError("Generated image not found", 404);
  const where = { imageId: generation.image.id };
  const [assets, total] = await prisma.$transaction([
    prisma.generatedImageAsset.findMany({ where, orderBy: { createdAt: "desc" }, skip: (query.page - 1) * query.limit, take: query.limit }),
    prisma.generatedImageAsset.count({ where }),
  ]);
  return { assets: assets.map(formatAsset), pagination: { page: query.page, limit: query.limit, total, totalPages: Math.ceil(total / query.limit) } };
};

export const getAssetById = async (userId: string, assetId: string) => {
  const asset = await prisma.generatedImageAsset.findFirst({ where: { id: assetId, image: { generation: { userId } } } });
  if (!asset) throw new AppError("Image asset not found", 404);
  return formatAsset(asset);
};

export const deleteAsset = async (userId: string, assetId: string): Promise<void> => {
  const asset = await prisma.generatedImageAsset.findFirst({ where: { id: assetId, image: { generation: { userId } } } });
  if (!asset) throw new AppError("Image asset not found", 404);
  await prisma.generatedImageAsset.delete({ where: { id: assetId } });
  if (!/^https?:\/\//i.test(asset.fileUrl)) await deleteFile(asset.fileUrl);
};
