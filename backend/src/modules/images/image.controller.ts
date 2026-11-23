import type { Request, Response, NextFunction } from "express";
import { getUserImages, getImageById, updateImage } from "./image.service.js";

export const getUserImagesController = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
  try {
    const result = await getUserImages(req.user!.userId, { page: Number(req.query.page ?? 1), limit: Number(req.query.limit ?? 10) });
    res.status(200).json({ success: true, message: "Images retrieved successfully", data: result });
  } catch (error) { next(error); }
};

export const getImageByIdController = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
  try {
    const image = await getImageById(req.user!.userId, req.params.id as string);
    res.status(200).json({ success: true, message: "Image retrieved successfully", data: { image } });
  } catch (error) { next(error); }
};

export const updateImageController = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
  try {
    const image = await updateImage(req.user!.userId, req.params.id as string, req.body);
    res.status(200).json({ success: true, message: "Image updated successfully", data: { image } });
  } catch (error) { next(error); }
};
