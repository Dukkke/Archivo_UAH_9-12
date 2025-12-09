from api_chatbot import search_documents, load_embeddings_and_documents

print("Running search debug...")
results, suggestions = search_documents("dictadura")
print(f"Results found: {len(results)}")
for r in results:
    print(f"Title: {r.get('title')} - Score: {r.get('relevance_score')}")

print("\nRunning search debug for 'hola'...")
results, suggestions = search_documents("hola")
print(f"Results found: {len(results)}")
