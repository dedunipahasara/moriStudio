import multer from "multer";
import path from "node:path";
import fs from "node:fs";
import crypto from "node:crypto";

import { env } from "../../config/env.js";

const uploadDirectory = path.resolve(
  env.STORAGE_PATH,
  "uploads",
  "images"
);

fs.mkdirSync(uploadDirectory, { recursive: true });

const allowedMimeTypes = [
  "image/jpeg",
  "image/png",
  "image/webp",
];

const storage = multer.diskStorage({
  destination: (_req, _file, callback) => {
    callback(null, uploadDirectory);
  },

  filename: (_req, file, callback) => {
    const extension = path.extname(file.originalname).toLowerCase();

    const filename = `${crypto.randomUUID()}${extension}`;

    callback(null, filename);
  },
});

const fileFilter: multer.Options["fileFilter"] = (
  _req,
  file,
  callback
) => {
  if (!allowedMimeTypes.includes(file.mimetype)) {
    callback(
      new Error("Only JPG, PNG and WEBP images are allowed.")
    );
    return;
  }

  callback(null, true);
};

export const uploadImage = multer({
  storage,
  fileFilter,
  limits: {
    fileSize: 10 * 1024 * 1024,
    files: 1,
  },
});
