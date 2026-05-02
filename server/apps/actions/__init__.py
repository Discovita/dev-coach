"""
Actions app.

Audit trail for coach-triggered actions. Provides the Action model,
read-only Django Admin, and ActionSerializer (consumed by UserViewSet
and TestUserViewSet — this app has no API endpoints of its own).
"""
