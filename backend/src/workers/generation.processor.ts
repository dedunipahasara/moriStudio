import { prisma } from "../config/prisma.js";
import { env } from "../config/env.js";
import { deleteFile, saveFile } from "../config/storage.js";

interface GenerationJobData {
  generationId: string;
  userId: string;
}

type SupportedMimeType =
  | "image/png"
  | "image/jpeg"
  | "image/webp";

interface AIEngineImage {
  image_base64?: string;
  imageBase64?: string;
  b64_json?: string;
  mime_type?: SupportedMimeType;
  mimeType?: SupportedMimeType;
  seed?: number;
}

interface AIEngineResponse {
  success?: boolean;
  image_base64?: string;
  imageBase64?: string;
  b64_json?: string;
  mime_type?: SupportedMimeType;
  mimeType?: SupportedMimeType;
  seed?: number;
  error?: string;
  detail?: string;
  data?: AIEngineImage | AIEngineImage[];
}

const MAX_IMAGE_BYTES = 15 * 1024 * 1024;
const AI_REQUEST_TIMEOUT_MS = 30 * 60 * 1000;

const decodeImage = (base64: string): Buffer => {
  // The AI Engine contract returns raw Base64, not a data URI.
  const normalized = base64.trim();

  if (
    !normalized ||
    normalized.length > Math.ceil(MAX_IMAGE_BYTES * 4 / 3) + 8 ||
    !/^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$/.test(normalized)
  ) {
    throw new Error("AI Engine returned invalid image Base64 data.");
  }

  const buffer = Buffer.from(normalized, "base64");

  if (
    buffer.length < 16 ||
    buffer.length > MAX_IMAGE_BYTES ||
    buffer.toString("base64") !== normalized
  ) {
    throw new Error("Generated image size or Base64 encoding is invalid.");
  }

  return buffer;
};

const detectImageExtension = (
  buffer: Buffer,
  mimeType?: string,
): { extension: "png" | "jpg" | "webp"; mimeType: SupportedMimeType } => {
  const isPng = buffer
    .subarray(0, 8)
    .equals(Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]));

  const isJpeg =
    buffer[0] === 0xff &&
    buffer[1] === 0xd8 &&
    buffer[2] === 0xff;

  const isWebp =
    buffer.toString("ascii", 0, 4) === "RIFF" &&
    buffer.toString("ascii", 8, 12) === "WEBP";

  if (isPng && (!mimeType || mimeType === "image/png")) {
    return { extension: "png", mimeType: "image/png" };
  }

  if (isJpeg && (!mimeType || mimeType === "image/jpeg")) {
    return { extension: "jpg", mimeType: "image/jpeg" };
  }

  if (isWebp && (!mimeType || mimeType === "image/webp")) {
    return { extension: "webp", mimeType: "image/webp" };
  }

  throw new Error(
    "AI Engine image bytes do not match a supported MIME type.",
  );
};

const readAIEngineResult = (
  payload: AIEngineResponse,
): {
  imageBase64: string;
  mimeType?: SupportedMimeType;
  seed?: number;
} => {
  // The Python backend currently returns snake_case fields directly:
  // generation_id, image_base64, mime_type, seed, ...
  // Accept camelCase as well for compatibility with wrapped API responses.
  const nested = Array.isArray(payload.data)
    ? payload.data[0]
    : payload.data;

  const imageBase64 =
    payload.image_base64 ??
    payload.imageBase64 ??
    payload.b64_json ??
    nested?.image_base64 ??
    nested?.imageBase64 ??
    nested?.b64_json;

  const mimeType =
    payload.mime_type ??
    payload.mimeType ??
    nested?.mime_type ??
    nested?.mimeType;

  const seed = payload.seed ?? nested?.seed;

  if (typeof imageBase64 !== "string" || !imageBase64) {
    throw new Error(
      payload.error ||
      payload.detail ||
      "AI Engine did not return image_base64.",
    );
  }

  if (
    mimeType !== undefined &&
    !["image/png", "image/jpeg", "image/webp"].includes(mimeType)
  ) {
    throw new Error("AI Engine returned an unsupported MIME type.");
  }

  if (
    seed !== undefined &&
    (!Number.isInteger(seed) || seed < 0 || seed > 2147483647)
  ) {
    throw new Error("AI Engine returned an invalid seed.");
  }

  return {
    imageBase64,
    mimeType,
    seed,
  };
};

const getAIEngineError = async (response: Response): Promise<string> => {
  const body = await response.text().catch(() => "");

  if (body) {
    try {
      const parsed = JSON.parse(body) as {
        detail?: string;
        error?: string;
        message?: string;
      };

      return (
        parsed.detail ||
        parsed.error ||
        parsed.message ||
        `AI Engine error: HTTP ${response.status}`
      );
    } catch {
      return body.slice(0, 500);
    }
  }

  return `AI Engine error: HTTP ${response.status}`;
};

export async function processGeneration(
  data: GenerationJobData,
): Promise<void> {
  const { generationId, userId } = data;
  let savedImagePath: string | undefined;

  try {
    const generation = await prisma.generation.findFirst({
      where: { id: generationId, userId },
      include: { image: { select: { id: true } } },
    });

    if (!generation) {
      throw new Error("Generation not found.");
    }

    // Idempotency: a retried BullMQ job must not generate or insert
    // a second image if a previous attempt already completed.
    if (
      generation.status === "COMPLETED" &&
      generation.image
    ) {
      return;
    }

    await prisma.generation.update({
      where: { id: generationId },
      data: {
        status: "PROCESSING",
        errorMessage: null,
      },
    });

    const baseUrl = env.AI_ENGINE_URL.replace(/\/+$/, "");
    const response = await fetch(`${baseUrl}/api/generations`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      // Match the FastAPI GenerationRequest schema.
      // Do not send generationId/userId unless the AI Engine schema
      // explicitly defines those fields.
      body: JSON.stringify({
        prompt: generation.prompt,
        style: generation.style ?? "auto",
        width: generation.width,
        height: generation.height,
        seed: generation.seed,
        negative_prompt: "",
      }),
      signal: AbortSignal.timeout(AI_REQUEST_TIMEOUT_MS),
    });

    if (!response.ok) {
      throw new Error(await getAIEngineError(response));
    }

    const result = await response.json() as AIEngineResponse;
    const parsed = readAIEngineResult(result);
    const imageBuffer = decodeImage(parsed.imageBase64);

    const detected = detectImageExtension(
      imageBuffer,
      parsed.mimeType,
    );

    savedImagePath = await saveFile(
      "images",
      imageBuffer,
      detected.extension,
    );

    const fileSize = BigInt(imageBuffer.byteLength);

    const imageWasCreated = await prisma.$transaction(async (tx) => {
      const existingImage = await tx.generatedImage.findUnique({
        where: { generationId },
        select: { id: true },
      });

      if (existingImage) {
        await tx.generation.update({
          where: { id: generationId },
          data: {
            status: "COMPLETED",
            seed: parsed.seed ?? generation.seed,
            errorMessage: null,
          },
        });

        return false;
      }

      await tx.generatedImage.create({
        data: {
          generationId,
          name: generation.prompt.slice(0, 150),
          description: generation.style
            ? `Style: ${generation.style}`
            : null,
          assets: {
            create: {
              type: "IMAGE",
              fileUrl: savedImagePath!,
              mimeType: detected.mimeType,
              fileSize,
            },
          },
        },
      });

      await tx.generation.update({
        where: { id: generationId },
        data: {
          status: "COMPLETED",
          seed: parsed.seed ?? generation.seed,
          errorMessage: null,
        },
      });

      return true;
    });

    // If another attempt already created the image, remove this
    // duplicate output file from local storage.
    if (!imageWasCreated && savedImagePath) {
      await deleteFile(savedImagePath);
      savedImagePath = undefined;
    }

    console.info(
      `Image generation completed: ${generationId}`,
    );
  } catch (error) {
    const message =
      error instanceof Error
        ? error.message
        : "Unknown image generation error.";

    if (savedImagePath) {
      await deleteFile(savedImagePath).catch(() => undefined);
    }

    await prisma.generation.updateMany({
      where: {
        id: generationId,
        userId,
        status: { not: "COMPLETED" },
      },
      data: {
        status: "FAILED",
        errorMessage: message.slice(0, 4000),
      },
    });

    console.error(
      `Image generation failed: ${generationId}`,
      message,
    );

    throw error;
  }
}
