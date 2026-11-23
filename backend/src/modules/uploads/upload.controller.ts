import type { Request, Response, NextFunction } from "express";
import { saveUploadedFile } from "./upload.service.js";

export const uploadImageController = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
  try {
    if (!req.file) { res.status(400).json({ success: false, message: "Please select an image to upload." }); return; }
    const uploadedFile = await saveUploadedFile(req.user!.userId, req.file);
    res.status(201).json({ success: true, message: "Reference image uploaded successfully.", data: { uploadedImage: uploadedFile } });
  } catch (error) { next(error); }
};
