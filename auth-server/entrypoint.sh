#!/bin/sh
set -e

echo "🚀 Starting Auth Server Entrypoint..."

# Wait for database to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
until node -e "require('child_process').execSync('npx prisma db execute --stdin --url=\"$DATABASE_URL\" <<< \"SELECT 1\"')"; do
  echo "   PostgreSQL is unavailable - sleeping"
  sleep 2
done

echo "✅ PostgreSQL is ready!"

# Run Prisma migrations
echo "🔄 Running database migrations..."
npx prisma migrate deploy

echo "✅ Migrations completed!"

# Start the server
echo "🎯 Starting auth server..."
exec node dist/index.js
