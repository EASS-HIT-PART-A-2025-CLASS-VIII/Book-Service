"""
LLM-powered book recommendations using Pydantic AI
"""
from pydantic import BaseModel, Field
from typing import List
import os


class BookRecommendation(BaseModel):
    """Single book recommendation with reasoning"""
    title: str = Field(description="Recommended book title")
    author: str = Field(description="Book author")
    reason: str = Field(description="Why this book is recommended (2-3 sentences)")
    similarity_score: float = Field(
        description="How similar to user's preferences (0-10)", 
        ge=0, 
        le=10
    )


class RecommendationResult(BaseModel):
    """Collection of book recommendations"""
    recommendations: List[BookRecommendation] = Field(
        description="List of recommended books", 
        max_length=5
    )
    reasoning: str = Field(description="Overall recommendation strategy")


# Check if OpenAI API key is available
HAS_OPENAI_KEY = bool(os.getenv("OPENAI_API_KEY"))

if HAS_OPENAI_KEY:
    from pydantic_ai import Agent
    
    recommendation_agent = Agent(
        'openai:gpt-4o-mini',
        result_tool=RecommendationResult,
        system_prompt="""
        You are an expert librarian and book recommendation specialist.
        
        Given a user's reading history (books they've rated highly), 
        recommend similar books they might enjoy.
        
        Consider:
        - Genre similarities
        - Writing style
        - Themes and topics
        - Author connections
        - Popularity and acclaim
        
        Provide thoughtful, personalized recommendations with clear reasoning.
        """,
    )
    print("✅ LLM Agent initialized successfully!")
else:
    recommendation_agent = None
    print("⚠️ No OPENAI_API_KEY found. LLM recommendations will use fallback mode.")


async def get_llm_recommendations(user_books: List[dict], available_books: List[dict]) -> RecommendationResult:
    """
    Get AI-powered book recommendations based on user's reading history.
    
    Args:
        user_books: List of books user has rated highly (with ratings > 7)
        available_books: All books in the library (to recommend from)
    
    Returns:
        RecommendationResult with AI-generated recommendations
    """
    if not HAS_OPENAI_KEY or recommendation_agent is None:
        raise Exception("OpenAI API key not configured")
    
    # Prepare prompt
    user_favorites = "\n".join([
        f"- {book['title']} by {book['author']} (Genre: {book['genre']}, Rating: {book.get('user_rating', 'N/A')})"
        for book in user_books
    ])
    
    available_titles = "\n".join([
        f"- {book['title']} by {book['author']} ({book['genre']})"
        for book in available_books
    ])
    
    prompt = f"""
    The user has enjoyed these books:
    {user_favorites}
    
    From this library catalog, recommend 5 books they would likely enjoy:
    {available_titles}
    
    Only recommend books from the catalog. Explain why each book matches their taste.
    """
    
    result = await recommendation_agent.run(prompt)
    return result.data


def get_simple_recommendations(user_books: List[dict], all_books: List[dict], limit: int = 5) -> List[dict]:
    """
    Simple rule-based recommendations (fallback when LLM is unavailable).
    
    Recommends books from same genres as user's favorites.
    """
    # Get user's favorite genres
    favorite_genres = {}
    for book in user_books:
        genre = book.get('genre', 'Fiction')
        favorite_genres[genre] = favorite_genres.get(genre, 0) + 1
    
    # Sort genres by frequency
    top_genres = sorted(favorite_genres.items(), key=lambda x: x[1], reverse=True)
    
    # Get user's book IDs to exclude
    user_book_ids = {book['id'] for book in user_books}
    
    # Recommend highly-rated books from favorite genres
    recommendations = []
    for genre, _ in top_genres:
        genre_books = [
            b for b in all_books 
            if b.get('genre') == genre 
            and b['id'] not in user_book_ids
            and b.get('average_rating', 0) >= 7
        ]
        recommendations.extend(sorted(
            genre_books, 
            key=lambda x: x.get('average_rating', 0), 
            reverse=True
        )[:2])
    
    # Fill remaining slots with top-rated books
    if len(recommendations) < limit:
        top_rated = sorted(
            [b for b in all_books if b['id'] not in user_book_ids],
            key=lambda x: x.get('average_rating', 0),
            reverse=True
        )
        recommendations.extend(top_rated[:limit - len(recommendations)])
    
    return recommendations[:limit]