export interface CreateGenerationInput {
  prompt: string;
  style?: string;
  width?: number;
  height?: number;
  seed?: number;
}

export interface GenerationQuery { page: number; limit: number; }
