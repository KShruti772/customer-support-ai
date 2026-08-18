from backend.app.rag.pipeline import RAGPipeline
import os

# Initialize RAGPipeline with our docs directory
pipeline = RAGPipeline(
    source_folder='D:\\customer-support-ai\\docs',
    index_path='D:\\customer-support-ai\\faiss.index',
    embedding_model_name='dummy',
    chunk_size=500,
    chunk_overlap=50
)

# Build the index
print('Building FAISS index...')
pipeline.build_index(rebuild=True)

# Test semantic search
print('\nTesting semantic search...')
results = pipeline.semantic_search('How much does the AstraCam X1 cost?', top_k=3)
print(f'Found {len(results)} results for price query:')
for i, r in enumerate(results):
    meta = r['metadata']
    score = r['score']
    text_preview = meta['text'][:80] + '...' if len(meta['text']) > 80 else meta['text']
    doc_id = meta.get('doc_id', 'unknown')
    output = f'  {i+1}. score={score:.3f}, doc={doc_id}: {text_preview}'
    print(output.encode('ascii', 'replace').decode('ascii'))

# Test another query
results2 = pipeline.semantic_search('How do I reset my password?', top_k=3)
print(f'\nFound {len(results2)} results for password reset query:')
for i, r in enumerate(results2):
    meta = r['metadata']
    text_preview = meta['text'][:80] + '...' if len(meta['text']) > 80 else meta['text']
    output = f'  {i+1}. score={r["score"]:.3f}: {text_preview}'
    print(output.encode('ascii', 'replace').decode('ascii'))

# Test empty query
results3 = pipeline.semantic_search('', top_k=3)
print(f'\nEmpty query returns {len(results3)} results')

# Test refund query
results4 = pipeline.semantic_search('refund policy', top_k=3)
print(f'\nFound {len(results4)} results for refund query:')
for i, r in enumerate(results4):
    meta = r['metadata']
    text_preview = meta['text'][:80] + '...' if len(meta['text']) > 80 else meta['text']
    output = f'  {i+1}. score={r["score"]:.3f}: {text_preview}'
    print(output.encode('ascii', 'replace').decode('ascii'))