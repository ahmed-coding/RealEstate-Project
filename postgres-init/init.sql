-- Enable pgvector extension for semantic search
CREATE EXTENSION IF NOT EXISTS vector;

-- Enable pg_trgm for trigram similarity search (autocomplete)
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Create hnsw vector index for faster similarity search (optional optimization)
-- This will be applied when creating PropertyEmbedding tables
