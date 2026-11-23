export interface ApiResponse<T = unknown> {
  success: boolean;
  message: string;
  data?: T;
  errors?: unknown;
}

export const successResponse = <T>(
  message: string,
  data?: T
): ApiResponse<T> => ({
  success: true,
  message,
  ...(data !== undefined && { data }),
});

export const errorResponse = (
  message: string,
  errors?: unknown
): ApiResponse => ({
  success: false,
  message,
  ...(errors !== undefined && { errors }),
});
