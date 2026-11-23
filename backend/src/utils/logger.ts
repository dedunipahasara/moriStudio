type LogLevel = "INFO" | "WARN" | "ERROR" | "DEBUG";

interface LogMetadata {
  [key: string]: unknown;
}

const log = (
  level: LogLevel,
  message: string,
  metadata?: LogMetadata
): void => {
  const timestamp = new Date().toISOString();

  const logEntry = {
    timestamp,
    level,
    message,
    ...(metadata && { metadata }),
  };

  switch (level) {
    case "ERROR":
      console.error(JSON.stringify(logEntry));
      break;

    case "WARN":
      console.warn(JSON.stringify(logEntry));
      break;

    default:
      console.log(JSON.stringify(logEntry));
  }
};

export const logger = {
  info: (message: string, metadata?: LogMetadata): void => {
    log("INFO", message, metadata);
  },

  warn: (message: string, metadata?: LogMetadata): void => {
    log("WARN", message, metadata);
  },

  error: (message: string, metadata?: LogMetadata): void => {
    log("ERROR", message, metadata);
  },

  debug: (message: string, metadata?: LogMetadata): void => {
    if (process.env.NODE_ENV === "development") {
      log("DEBUG", message, metadata);
    }
  },
};
