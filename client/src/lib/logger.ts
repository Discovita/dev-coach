export enum LogLevel {
  ERROR = 0,
  WARN = 1,
  INFO = 2,
  DEBUG = 3,
  TRACE = 4
}

export class Logger {
  private name: string;
  private level: LogLevel;

  constructor(name: string, level: LogLevel = LogLevel.INFO) {
    this.name = name;
    this.level = level;
  }

  setLevel(level: LogLevel): void {
    this.level = level;
  }

  private getCallerFunction(): string {
    const stack = new Error().stack;
    if (!stack) return '';
    
    const lines = stack.split('\n');
    const callerLine = lines[3]; // Skips Error, getCallerFunction, and the log method
    
    if (!callerLine) return '';
    
    // Extract just the function name
    const match = callerLine.match(/at (?:.*\.)?(\w+)/);
    return match ? match[1] : 'anonymous';
  }

  error(...args: unknown[]): void {
    if (this.level >= LogLevel.ERROR) {
      const func = this.getCallerFunction();
      console.error(`\x1b[31mERROR\x1b[0m:\t  [${this.name}:${func}]`, ...args);
    }
  }

  warn(...args: unknown[]): void {
    if (this.level >= LogLevel.WARN) {
      const func = this.getCallerFunction();
      console.warn(`\x1b[33mWARNING\x1b[0m:  [${this.name}:${func}]`, ...args);
    }
  }

  info(...args: unknown[]): void {
    if (this.level >= LogLevel.INFO) {
      const func = this.getCallerFunction();
      console.info(`\x1b[32mINFO\x1b[0m:\t  [${this.name}:${func}]`, ...args);
    }
  }

  debug(...args: unknown[]): void {
    if (this.level >= LogLevel.DEBUG) {
      const func = this.getCallerFunction();
      console.log(`%cDEBUG%c:\t  [${this.name}:${func}]`, 'color:#888', '', ...args);
    }
  }

  trace(...args: unknown[]): void {
    if (this.level >= LogLevel.TRACE) {
      const func = this.getCallerFunction();
      console.log(`\x1b[34mTRACE\x1b[0m:\t  [${this.name}:${func}]`, ...args);
    }
  }
}

export const createLogger = (name: string, level: LogLevel = LogLevel.INFO): Logger => {
  return new Logger(name, level);
};