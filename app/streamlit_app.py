import streamlit as st
import requests
import uuid
import os
from PIL import Image

# API configuration
API_URL = "http://localhost:8000"

# Generate or retrieve user ID
if 'user_id' not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

# Initialize view mode
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = 'gallery'  # 'gallery' or 'details'
if 'selected_book_id' not in st.session_state:
    st.session_state.selected_book_id = None

# Page config
st.set_page_config(
    page_title="Book Library",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
page_style = """
<style>
body {
    background-color: #fffafc;
}
.stApp {
    background-color: #fffafc;
}
.book-card {
    background: transparent !important;
    border-radius: 15px;
    padding: 15px;
    text-align: center;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    height: 100%;
    position: relative;
}
.book-card:hover {
    transform: translateY(-5px);
}
.book-image {
    width: 100%;
    height: 280px;
    object-fit: cover;
    border-radius: 10px;
    margin-bottom: 10px;
}
.book-title {
    font-size: 0.95em;
    font-weight: bold;
    color: #333;
    margin: 10px 0 5px 0;
    min-height: 45px;
    display: flex;
    align-items: center;
    justify-content: center;
}
.book-author {
    color: #666;
    font-size: 0.85em;
    margin-bottom: 10px;
}
.book-rating {
    color: #FFD700;
    font-size: 0.9em;
    margin: 5px 0;
}
.card-buttons {
    position: absolute;
    top: 10px;
    right: 10px;
    display: flex;
    gap: 5px;
}

/* Sidebar logo */
section[data-testid="stSidebar"] img {
    background: transparent !important;
}
.sidebar-logo {
    display: block;
    margin: -40px auto 5px auto;
}
</style>
"""
st.markdown(page_style, unsafe_allow_html=True)

# Function to go to details
def view_book_details(book_id):
    st.session_state.view_mode = 'details'
    st.session_state.selected_book_id = book_id

# Function to go back to gallery
def back_to_gallery():
    st.session_state.view_mode = 'gallery'
    st.session_state.selected_book_id = None

# Sidebar (only in gallery mode)
if st.session_state.view_mode == 'gallery':
    with st.sidebar:
        st.markdown(
        """
        <div style="text-align: center; margin-bottom: 10px;">
            <img src="https://cdn-icons-png.flaticon.com/512/6475/6475888.png" 
                 style="width:150px; height:auto; border-radius: 15px;">
        </div>
        """,
        unsafe_allow_html=True
        )
        
        st.markdown("""
            <div style='text-align: center; font-family: "Arial Black", Gadget, sans-serif; font-size: 1.8em; font-weight: bold; white-space: nowrap; margin-bottom: 5px;'>
                Book Library
            </div>
            <div style='text-align: left; font-style: italic; color: #888; font-size: 0.85em; margin-top: -10px;'>
                by Shiri Barzilay
            </div>
            """, unsafe_allow_html=True
        )

        st.markdown("---")
        
        # Search
        search_query = st.text_input("🔍 Search", placeholder="Search by title or author...")
        
        # Genre filter
        st.subheader("Filter by Genre")
        genre_options = ["All", "Historical Fiction", "Fantasy", "Romance", "Dystopian", 
                         "Fiction", "Mystery", "Thriller", "Science Fiction", "Biography"]
        selected_genre = st.selectbox("Genre", genre_options, label_visibility="collapsed")
        
        # View options
        st.markdown("---")
        st.subheader("View")
        view_option = st.radio("", ["All Books", "My Favorites", "Top Rated"], label_visibility="collapsed")
else:
    search_query = ""
    selected_genre = "All"
    view_option = "All Books"
# Fetch books
try:
    response = requests.get(f"{API_URL}/books")
    if response.status_code == 200:
        all_books = response.json()
        books = all_books.copy()
        
        # GALLERY MODE
        if st.session_state.view_mode == 'gallery':
            # Filter by search
            if search_query:
                books = [b for b in books if 
                        search_query.lower() in b.get("title", "").lower() or 
                        search_query.lower() in b.get("author", "").lower()]
            
            # Filter by genre
            if selected_genre != "All":
                books = [b for b in books if b.get("genre") == selected_genre]
            
            # Filter by view option
            if view_option == "My Favorites":
                books = [b for b in books if st.session_state.user_id in b.get("favorites", [])]
            elif view_option == "Top Rated":
                books = [b for b in books if b.get("average_rating", 0) >= 7]
                books = sorted(books, key=lambda x: x.get("average_rating", 0), reverse=True)
            
            # Display books in gallery
            # Header with book count
            header_col1, header_col2 = st.columns([3, 1])
            with header_col1:
                st.markdown("### 📖 Library")
            with header_col2:
                st.markdown(f"<p style='text-align: right; color: #888; font-size: 0.85em; margin-top: 10px;'>{len(books)} books</p>", unsafe_allow_html=True)
            
            if books:
                # Create grid layout
                cols_per_row = 5
                for i in range(0, len(books), cols_per_row):
                    cols = st.columns(cols_per_row)
                    for idx, book in enumerate(books[i:i+cols_per_row]):
                        with cols[idx]:
                            # Card container - buttons side by side
                            button_col1, button_col2 = st.columns(2)
                            
                            with button_col1:
                                if st.button("🔍", key=f"view_{book['id']}", help="View details", use_container_width=True):
                                    view_book_details(book['id'])
                                    st.rerun()
                            
                            with button_col2:
                                is_favorite = st.session_state.user_id in book.get("favorites", [])
                                fav_icon = "❤️" if is_favorite else "🤍"
                                if st.button(fav_icon, key=f"fav_{book['id']}", help="Favorite", use_container_width=True):
                                    requests.post(f"{API_URL}/books/{book['id']}/favorite", 
                                                params={"user_id": st.session_state.user_id})
                                    st.rerun()
                            
                            # Book card
                            st.markdown(f"""
                            <div class='book-card'>
                                <img src='{book["image_url"]}' class='book-image'/>
                                <div class='book-title'>{book["title"]}</div>
                                <div class='book-author'>{book["author"]}</div>
                                <div class='book-rating'>⭐ {book.get("average_rating", 0):.1f}/10</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Rating below card
                            user_rating = book.get("user_ratings", {}).get(st.session_state.user_id, 0.0)
                            new_rating = st.slider("", 0.0, 10.0, float(user_rating), 0.5, 
                                                  key=f"rate_{book['id']}")
                            
                            if new_rating != user_rating:
                                if st.button("Rate ✓", key=f"submit_{book['id']}"):
                                    requests.post(f"{API_URL}/books/{book['id']}/rate",
                                                params={"user_id": st.session_state.user_id, "rating": new_rating})
                                    st.rerun()
            else:
                st.info("No books found. Try adjusting your filters!")
            
            # Most Recommended at bottom
            max_rating = max((b.get("average_rating", 0) for b in all_books), default=0)
            if max_rating > 0:
                top_books = [b for b in all_books if b.get("average_rating", 0) == max_rating]
                
                st.markdown("---")
                st.markdown("#### 🏆 Most Recommended")
                
                top_cols = st.columns(min(len(top_books), 5))
                for idx, book in enumerate(top_books[:5]):
                    with top_cols[idx]:
                        st.markdown(f"""
                        <div style='text-align: center; padding: 10px; background: white; border-radius: 10px;'>
                            <img src='{book["image_url"]}' style='width: 100px; border-radius: 8px;'/>
                            <p style='font-size: 0.85em; font-weight: bold; margin: 8px 0 2px 0;'>{book["title"]}</p>
                            <p style='color: #666; font-size: 0.75em; margin: 0;'>{book["author"]}</p>
                            <p style='color: #FFD700; font-size: 0.85em; margin: 5px 0 0 0;'>⭐ {book["average_rating"]:.1f}/10</p>
                        </div>
                        """, unsafe_allow_html=True)
        
        # DETAILS MODE
        elif st.session_state.view_mode == 'details' and st.session_state.selected_book_id:
            book = next((b for b in all_books if b['id'] == st.session_state.selected_book_id), None)
            
            if book:
                # Back button at top
                if st.button("← Back to Library"):
                    back_to_gallery()
                    st.rerun()
                
                st.markdown("---")
                st.markdown("## 📖 Book Details")
                
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.image(book["image_url"], use_container_width=True)
                
                with col2:
                    st.markdown(f"# {book['title']}")
                    st.markdown(f"**By {book['author']}**")
                    st.markdown(f"**Genre:** {book['genre']}")
                    
                    avg_rating = book.get("average_rating", 0)
                    total_ratings = book.get("total_ratings", 0)
                    st.markdown(f"**Average Rating:** ⭐ {avg_rating:.1f}/10 ({total_ratings} ratings)")
                    
                    st.markdown("### About this book")
                    st.write(book.get("description", "No description available."))
            else:
                st.error("Book not found")
                if st.button("← Back to Library"):
                    back_to_gallery()
                    st.rerun()
        
    else:
        st.error("Failed to load books")
        
except requests.exceptions.ConnectionError:
    st.error("⚠️ Cannot connect to API. Make sure the FastAPI server is running!")