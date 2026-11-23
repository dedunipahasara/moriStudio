import { prisma } from "../../config/prisma.js";
import { AppError } from "../../utils/app-error.js";

export interface UpdateUserInput {
  name: string;
}

// ==========================================
// GET USER PROFILE
// ==========================================

export const getUserProfile = async (userId: string) => {
  const user = await prisma.user.findUnique({
    where: {
      id: userId,
    },
    select: {
      id: true,
      name: true,
      email: true,
      emailVerifiedAt: true,
      createdAt: true,
      updatedAt: true,
    },
  });

  if (!user) {
    throw new AppError("User not found", 404);
  }

  return user;
};

// ==========================================
// UPDATE USER PROFILE
// ==========================================

export const updateUserProfile = async (
  userId: string,
  data: UpdateUserInput
) => {
  const existingUser = await prisma.user.findUnique({
    where: {
      id: userId,
    },
    select: {
      id: true,
    },
  });

  if (!existingUser) {
    throw new AppError("User not found", 404);
  }

  const updatedUser = await prisma.user.update({
    where: {
      id: userId,
    },
    data: {
      name: data.name.trim(),
    },
    select: {
      id: true,
      name: true,
      email: true,
      emailVerifiedAt: true,
      createdAt: true,
      updatedAt: true,
    },
  });

  return updatedUser;
};
