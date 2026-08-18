from backend.app.services.chat_service import ChatService

# Test that ChatService initializes with RAGPipeline
cs = ChatService()
print(f'ChatService rag type: {type(cs.rag).__name__}')
print(f'RAGPipeline has semantic_search: {hasattr(cs.rag, "semantic_search")}')

# Test chat endpoint basic functionality
result = cs.chat(user_id='test_user', message='How much does the AstraCam X1 cost?')
print(f'\nChat result final_answer: {result.final_answer[:100]}...')
print(f'Chat result escalate: {result.escalate}')
print(f'Chat result sources: {result.sources}')