#!/bin/bash
# Start PostgreSQL container for local development

docker run -d \
  --name swiftfab-postgres \
  -e POSTGRES_USER=swiftfab \
  -e POSTGRES_PASSWORD=swiftfab123 \
  -e POSTGRES_DB=swiftfab \
  -p 5432:5432 \
  --restart unless-stopped \
  postgres:15-alpine

echo "PostgreSQL started on localhost:5432"
echo "Database: swiftfab"
echo "User: swiftfab"
echo "Password: swiftfab123"
echo ""
echo "Connection string:"
echo "postgresql://swiftfab:swiftfab123@localhost:5432/swiftfab"

