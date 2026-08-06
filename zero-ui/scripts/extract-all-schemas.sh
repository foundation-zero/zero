#!/bin/bash

# Script to extract all schema values and generate GraphQL queries for all modules
# Usage: ./scripts/extract-all-schemas.sh

echo "🚀 Starting extraction of all schema values and generation of GraphQL queries..."

pnpm run extract-all-schemas
