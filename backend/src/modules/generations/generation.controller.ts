import type { Request, Response, NextFunction } from "express";

import {
  createGeneration,
  getUserGenerations,
  getGenerationById,
} from "./generation.service.js";

import type {
  CreateGenerationInput,
  GenerationQuery,
} from "./generation.types.js";

// ==========================================
// CREATE GENERATION
// ==========================================

export const createGenerationController = async (
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> => {
  try {
    const generation = await createGeneration(
      req.user!.userId,
      req.body as CreateGenerationInput
    );

    res.status(201).json({
      success: true,
      message: "Generation request created successfully",
      data: {
        generation,
      },
    });
  } catch (error) {
    next(error);
  }
};

// ==========================================
// GET USER GENERATIONS
// ==========================================

export const getUserGenerationsController = async (
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> => {
  try {
    const page = Number(req.query.page ?? 1);
    const limit = Number(req.query.limit ?? 10);

    const result = await getUserGenerations(
      req.user!.userId,
      { page, limit } as GenerationQuery
    );

    res.status(200).json({
      success: true,
      message: "Generation history retrieved successfully",
      data: result,
    });
  } catch (error) {
    next(error);
  }
};

// ==========================================
// GET SINGLE GENERATION
// ==========================================

export const getGenerationByIdController = async (
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> => {
  try {
    const generation = await getGenerationById(
      req.user!.userId,
      req.params.id as string
    );

    res.status(200).json({
      success: true,
      message: "Generation details retrieved successfully",
      data: {
        generation,
      },
    });
  } catch (error) {
    next(error);
  }
};
