"""
Coach app.

Provides the coaching chatbot API — accepts user messages, orchestrates
AI response generation via the CoachService, and returns structured
coach responses. No models; this app is a thin API layer over the
coach_service and the chat_messages app.
"""
