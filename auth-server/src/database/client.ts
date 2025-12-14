import { PrismaClient } from '@prisma/client';

declare global {
  // eslint-disable-next-line no-var
  var prisma: PrismaClient | undefined;
}

// Lazy initialize Prisma Client
let _prisma: PrismaClient | undefined;

function getPrismaClient(): PrismaClient {
  if (_prisma) {
    return _prisma;
  }

  if (global.prisma) {
    _prisma = global.prisma;
    return _prisma;
  }

  _prisma = new PrismaClient({
    log: ['query', 'info', 'warn', 'error'],
  });

  if (process.env.NODE_ENV !== 'production') {
    global.prisma = _prisma;
  }

  return _prisma;
}

// Export Proxy that lazily initializes on first access
export const prisma = new Proxy({} as PrismaClient, {
  get(target, prop) {
    const client = getPrismaClient();
    const value = client[prop as keyof PrismaClient];

    // Bind methods to the client instance
    if (typeof value === 'function') {
      return value.bind(client);
    }

    return value;
  }
});

export default prisma;