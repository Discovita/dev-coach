"""
Chat messages app.

Stores the conversation history between users and the coaching chatbot.
Provides the ChatMessage model, ChatMessageSerializer, initial message
constants, and a post_save signal that triggers user notes extraction.

This app has no API endpoints of its own — messages are read and created
through UserViewSet, TestUserViewSet, and the coach service.
"""
