
"""
Recommender Module

This module provides fitness and nutrition recommendations based on user input.
It includes calorie calculation, workout suggestions, and meal recommendations.
"""

from .service import recommender_service
from .routes import router

__all__ = ["recommender_service", "router"]