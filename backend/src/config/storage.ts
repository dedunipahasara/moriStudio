import { mkdir, writeFile, unlink, access } from "node:fs/promises";
import path from "node:path";
import { randomUUID } from "node:crypto";
import { env } from "./env.js";

export const STORAGE_DIRECTORIES = {
  IMAGES: "images",
  THUMBNAILS: "thumbnails",
  UPLOADS: "uploads/images",
  TEMP: "temp",
} as const;
export type StorageDirectory = (typeof STORAGE_DIRECTORIES)[keyof typeof STORAGE_DIRECTORIES];
export const STORAGE_ROOT = path.resolve(env.STORAGE_PATH);

export const initializeStorage = async (): Promise<void> => {
  await Promise.all(Object.values(STORAGE_DIRECTORIES).map((directory) => mkdir(path.join(STORAGE_ROOT, directory), { recursive: true })));
};
export const getStorageDirectory = (directory: StorageDirectory): string => path.join(STORAGE_ROOT, directory);
export const generateFileName = (extension: string): string => {
  const safeExtension = extension.replace(/^\./, "").toLowerCase();
  if (!/^[a-z0-9]+$/.test(safeExtension)) throw new Error("Invalid file extension");
  return `${randomUUID()}.${safeExtension}`;
};
export const saveFile = async (directory: StorageDirectory, buffer: Buffer, extension: string): Promise<string> => {
  const folderPath = getStorageDirectory(directory);
  await mkdir(folderPath, { recursive: true });
  const fileName = generateFileName(extension);
  await writeFile(path.join(folderPath, fileName), buffer, { flag: "wx" });
  return path.posix.join(directory, fileName);
};
export const getStorageFilePath = (relativePath: string): string => {
  const resolvedPath = path.resolve(STORAGE_ROOT, relativePath);
  const relative = path.relative(STORAGE_ROOT, resolvedPath);
  if (!relative || relative.startsWith("..") || path.isAbsolute(relative)) throw new Error("Invalid storage file path");
  return resolvedPath;
};
export const storageFileExists = async (relativePath: string): Promise<boolean> => {
  try { await access(getStorageFilePath(relativePath)); return true; } catch { return false; }
};
export const deleteFile = async (relativePath: string): Promise<void> => {
  try { await unlink(getStorageFilePath(relativePath)); }
  catch (error) {
    if (typeof error === "object" && error !== null && "code" in error && error.code === "ENOENT") return;
    throw error;
  }
};
