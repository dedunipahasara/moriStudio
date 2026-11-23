import express, { type Express } from "express";
import { prisma } from "./config/prisma.js";
import { corsMiddleware } from "./config/cors.js";
import { errorMiddleware } from "./middleware/error.middleware.js";
import authRoutes from "./modules/auth/auth.routes.js";
import passwordRoutes from "./modules/password/password.routes.js";
import verificationRoutes from "./modules/email-verification/verification.routes.js";
import userRoutes from "./modules/users/user.routes.js";
import generationRoutes from "./modules/generations/generation.routes.js";
import uploadRoutes from "./modules/uploads/upload.routes.js";
import imageRoutes from "./modules/images/image.routes.js";
import assetRoutes from "./modules/assets/asset.routes.js";

const app: Express = express();
app.use(corsMiddleware);
app.use(express.json({ limit: "2mb" }));
app.use(express.urlencoded({ extended: true }));

app.get("/health", async (_req, res) => {
  try {
    await prisma.$queryRaw`SELECT 1`;
    res.status(200).json({ success: true, message: "Cute3D Studio Image API is running", database: "connected", timestamp: new Date().toISOString() });
  } catch (error) {
    console.error("Health check failed:", error);
    res.status(503).json({ success: false, message: "Database connection failed", database: "disconnected" });
  }
});

app.use("/api/auth", authRoutes);
app.use("/api/password", passwordRoutes);
app.use("/api/email-verification", verificationRoutes);
app.use("/api/users", userRoutes);
app.use("/api/generations", generationRoutes);
app.use("/api/uploads", uploadRoutes);
app.use("/api/images", imageRoutes);
app.use("/api/assets", assetRoutes);

app.use((_req, res) => res.status(404).json({ success: false, message: "API endpoint not found" }));
app.use(errorMiddleware);
export default app;
