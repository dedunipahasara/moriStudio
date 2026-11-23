import type { Request, Response, NextFunction } from "express";
import { getGenerationAssets, getAssetById, deleteAsset } from "./asset.service.js";
import { getStorageFilePath } from "../../config/storage.js";

export const getGenerationAssetsController = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
  try {
    const result = await getGenerationAssets(req.user!.userId, req.params.generationId as string, { page: Number(req.query.page ?? 1), limit: Number(req.query.limit ?? 10) });
    res.status(200).json({ success: true, message: "Image assets retrieved successfully", data: result });
  } catch (error) { next(error); }
};
export const getAssetByIdController = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
  try { const asset = await getAssetById(req.user!.userId, req.params.id as string); res.status(200).json({ success: true, message: "Image asset retrieved successfully", data: { asset } }); }
  catch (error) { next(error); }
};
export const deleteAssetController = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
  try { await deleteAsset(req.user!.userId, req.params.id as string); res.status(200).json({ success: true, message: "Image asset deleted successfully" }); }
  catch (error) { next(error); }
};

export const getAssetFileController = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
  try {
    const asset = await getAssetById(req.user!.userId, req.params.id as string);
    const filePath = getStorageFilePath(asset.fileUrl);
    res.type(asset.mimeType ?? "application/octet-stream");
    res.sendFile(filePath, (error) => { if (error && !res.headersSent) next(error); });
  } catch (error) { next(error); }
};
