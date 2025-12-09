"""
Script OPTIMIZADO para regenerar embeddings - procesamiento en lotes grandes
"""
import json
import pickle
import google.generativeai as genai
from dotenv import load_dotenv
import os
import time

load_dotenv()

# Nueva API key
GEMINI_API_KEY = "AIzaSyA2lW29n_lB4l1BWNljUqaf9jnIct8QI-o"
genai.configure(api_key=GEMINI_API_KEY)

def load_documents():
    with open('clean_with_metadata.json', 'r', encoding='utf-8', errors='ignore') as f:
        docs = json.load(f)
    print(f"📂 {len(docs)} documentos cargados")
    return docs

def process_batch(batch_start, batch):
    """Procesa un lote de documentos"""
    texts = []
    indices = []
    
    for i, doc in enumerate(batch):
        idx = batch_start + i
        text = doc.get('title', '')[:200]
        texts.append(text if text else "documento")
        indices.append(idx)
    
    try:
        result = genai.embed_content(
            model="models/embedding-001",
            content=texts,
            task_type="retrieval_document"
        )
        return [(indices[i], emb) for i, emb in enumerate(result['embedding'])]
    except Exception as e:
        print(f"⚠️ Error lote {batch_start}: {e}")
        return []

def create_embeddings_fast(documents):
    embeddings = {}
    total = len(documents)
    batch_size = 100
    
    print(f"🚀 Generando embeddings para {total} docs (lotes de {batch_size})...")
    
    processed = 0
    for i in range(0, total, batch_size):
        batch = documents[i:i+batch_size]
        results = process_batch(i, batch)
        for idx, emb in results:
            embeddings[idx] = emb
        processed += len(batch)
        
        if processed % 1000 == 0 or processed == total:
            print(f"   ✅ {processed}/{total} ({100*processed/total:.0f}%)")
        
        time.sleep(0.3)
    
    return embeddings

if __name__ == "__main__":
    print("=" * 40)
    print("🔄 REGENERACIÓN OPTIMIZADA DE EMBEDDINGS")
    print("=" * 40)
    
    start = time.time()
    documents = load_documents()
    embeddings = create_embeddings_fast(documents)
    
    with open('embeddings_cache.pkl', 'wb') as f:
        pickle.dump(embeddings, f)
    
    elapsed = time.time() - start
    print("=" * 40)
    print(f"✅ COMPLETADO en {elapsed/60:.1f} minutos")
    print(f"   Embeddings: {len(embeddings)}")
    print("=" * 40)
