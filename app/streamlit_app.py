import streamlit as st
import requests
import uuid
import os
import base64
from pathlib import Path

# API configuration - use environment variable for Docker
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Generate or retrieve user ID - use query params to persist across refreshes
import streamlit as st
from streamlit import query_params

def get_base64_image(image_path):
    """Convert local image to base64"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None
        
# Try to get user_id from URL query params
params = st.query_params
if 'user_id' in params:
    user_id = params['user_id']
else:
    # Generate new user_id and add to URL
    user_id = str(uuid.uuid4())
    st.query_params['user_id'] = user_id

# Store in session state
if 'user_id' not in st.session_state:
    st.session_state.user_id = user_id

# Initialize view mode
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = 'gallery'
if 'selected_book_id' not in st.session_state:
    st.session_state.selected_book_id = None
if 'selected_genre' not in st.session_state:
    st.session_state.selected_genre = "All"
if 'view_filter' not in st.session_state:
    st.session_state.view_filter = "All Books"

# Page config
st.set_page_config(
    page_title="Book Library",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
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

/* Hide sidebar */
[data-testid="stSidebar"] {
    display: none;
}

/* Header section */
.header-container {
    background: white;
    padding: 20px 50px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    margin-bottom: 30px;
}

.logo-section {
    text-align: center;
}

.logo {
    font-size: 2.5em;
    font-weight: bold;
    color: #e91e63;
    display: inline-block;
}

.subtitle {
    font-style: italic;
    color: #888;
    font-size: 0.9em;
    margin-top: 5px;
}

/* About Us section */
.about-container {
    background: white;
    padding: 40px;
    border-radius: 15px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    margin: 30px auto;
    max-width: 800px;
}

.about-title {
    font-size: 2em;
    font-weight: bold;
    color: #e91e63;
    text-align: center;
    margin-bottom: 20px;
}

.about-text {
    font-size: 1.1em;
    line-height: 1.8;
    color: #333;
    text-align: center;
}

/* Navigation buttons */
.nav-button {
    background: transparent;
    border: none;
    font-size: 1.1em;
    padding: 10px 20px;
    cursor: pointer;
    transition: background 0.3s;
    border-radius: 5px;
}

.nav-button:hover {
    background: #f5f5f5;
}

/* Dropdown styling */
.dropdown-container {
    background: white;
    padding: 30px;
    border-radius: 10px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    margin: 20px auto;
    max-width: 900px;
}

/* Book cards */
.book-card-container {
    background: white;
    border-radius: 15px;
    padding: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    margin-bottom: 15px;
}

.book-card-container:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.15);
}

.book-image {
    width: 100%;
    height: 280px;
    object-fit: cover;
    border-radius: 10px;
    margin-bottom: 8px;
}

.book-title {
    font-size: 0.95em;
    font-weight: bold;
    color: #333;
    margin: 8px 0 4px 0;
    min-height: 40px;
    text-align: center;
}

.book-author {
    color: #666;
    font-size: 0.85em;
    margin: 4px 0;
    text-align: center;
}

.book-rating {
    color: #FFD700;
    font-size: 0.9em;
    margin: 4px 0 8px 0;
    text-align: center;
}
/* Navigation menu buttons - compact */
[data-testid="column"] .stButton > button {
    padding: 8px 2px !important;
    font-size: 0.9em !important;
}

/* Button styling */
.stButton > button {
    background: transparent !important;
    border: none !important;
    padding: 4px !important;
    font-size: 1.4em !important;
    transition: transform 0.2s !important;
}

.stButton > button:hover {
    transform: scale(1.15) !important;
}

/* Slider styling */
.stSlider {
    margin-top: 5px !important;
}

/* Row separator */
.row-separator {
    border-top: 2px solid #f0f0f0;
    margin: 30px 0;
}

/* Genre menu styling */
.genre-menu-header {
    text-align: center;
    font-size: 1.5em;
    font-weight: bold;
    color: #e91e63;
    margin-bottom: 20px;
}

.close-button {
    text-align: center;
    margin-bottom: 20px;
}
</style>
"""
st.markdown(page_style, unsafe_allow_html=True)

# Functions
def view_book_details(book_id):
    st.session_state.view_mode = 'details'
    st.session_state.selected_book_id = book_id

def back_to_gallery():
    st.session_state.view_mode = 'gallery'
    st.session_state.selected_book_id = None

# Quote at the very top with separator
st.markdown("""
<div style='text-align: center; padding: 0px 0 15px 0; margin: 0;'>
    <div style='font-size: 1.3em; font-style: italic; color: #2c3e50; font-weight: 400; font-family: "Georgia", "Garamond", "Times New Roman", serif; line-height: 1.6;'>
        "Today a reader, tomorrow a leader."
    </div>
    <div style='font-size: 0.95em; color: #34495e; margin-top: 10px; font-family: "Georgia", serif; letter-spacing: 1px;'>
        — Margaret Fuller
    </div>
</div>
<hr style='border: none; border-top: 2px solid #e91e63; width: 60%; margin: 0 auto 30px auto;'>
""", unsafe_allow_html=True)

# Header with logo using columns
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("""
    <div style='text-align: center;'>
        <div style='font-size: 2.5em; font-weight: bold; color: #e91e63;'> Book Library</div>
        <div style='font-style: italic; color: #888; font-size: 0.9em; margin-top: 5px;'>by Shiri Barzilay</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    logo_path = Path(__file__).parent / "images" / "ספרים.png"
    if logo_path.exists():
        st.image(str(logo_path), width=120)

# Cart button (top left)
cart_col1, cart_col2, cart_col3 = st.columns([1, 4, 1])
with cart_col1:
    # Get cart count
    try:
        cart_response = requests.get(f"{API_URL}/books/cart/{st.session_state.user_id}")
        cart_count = len(cart_response.json()) if cart_response.status_code == 200 else 0
    except:
        cart_count = 0
    
    if st.button(f"🛒 My Orders ({cart_count})", key="cart_btn"):
        st.session_state.view_mode = 'cart'
        st.rerun()

# Search bar (centered)
search_col1, search_col2, search_col3 = st.columns([1, 2, 1])
with search_col2:
    search_query = st.text_input("", placeholder="🔍 Search by title or author...", key="search_input", label_visibility="collapsed")

st.markdown("<br>", unsafe_allow_html=True)

# Navigation menu with pink dividers
nav_cols = st.columns([0.6, 0.02, 0.5, 0.02, 0.4, 0.02, 0.45, 0.02, 0.6, 0.02, 0.7, 0.02, 1])

with nav_cols[0]:
    if st.button("ℹ️ About Us", key="about_btn", use_container_width=True):
        st.session_state.view_mode = 'about'
        st.session_state.show_genre_menu = False
        st.rerun()

with nav_cols[1]:
    st.markdown("<div style='border-left: 1px solid #e91e63; height: 25px; margin: auto;'></div>", unsafe_allow_html=True)

with nav_cols[2]:
    if st.button("📚 Books", key="books_btn", use_container_width=True):
        st.session_state.show_genre_menu = not st.session_state.get('show_genre_menu', False)
        st.session_state.view_mode = 'gallery'

with nav_cols[3]:
    st.markdown("<div style='border-left: 1px solid #e91e63; height: 25px; margin: auto;'></div>", unsafe_allow_html=True)

with nav_cols[4]:
    if st.button("👶 Kids", key="children_btn", use_container_width=True):
        st.session_state.selected_genre = "Children"
        st.session_state.view_filter = "All Books"
        st.session_state.show_genre_menu = False
        st.session_state.view_mode = 'gallery'
        st.rerun()

with nav_cols[5]:
    st.markdown("<div style='border-left: 1px solid #e91e63; height: 25px; margin: auto;'></div>", unsafe_allow_html=True)

with nav_cols[6]:
    if st.button("🏆 Top", key="recommended_btn", use_container_width=True):
        st.session_state.view_filter = "Top Rated"
        st.session_state.selected_genre = "All"
        st.session_state.show_genre_menu = False
        st.session_state.view_mode = 'gallery'
        st.rerun()

with nav_cols[7]:
    st.markdown("<div style='border-left: 1px solid #e91e63; height: 25px; margin: auto;'></div>", unsafe_allow_html=True)

with nav_cols[8]:
    if st.button("❤️ Favorites", key="favorites_btn", use_container_width=True):
        st.session_state.view_filter = "My Favorites"
        st.session_state.selected_genre = "All"
        st.session_state.show_genre_menu = False
        st.session_state.view_mode = 'gallery'
        st.rerun()

with nav_cols[9]:
    st.markdown("<div style='border-left: 1px solid #e91e63; height: 25px; margin: auto;'></div>", unsafe_allow_html=True)

with nav_cols[10]:
    if st.button("🌟 Weekly Top", key="weekly_btn", use_container_width=True):
        st.session_state.view_mode = 'weekly'
        st.session_state.show_genre_menu = False
        st.rerun()

with nav_cols[11]:
    st.markdown("<div style='border-left: 1px solid #e91e63; height: 25px; margin: auto;'></div>", unsafe_allow_html=True)

with nav_cols[12]:
    if st.button("🎯 Recommended for you", key="ai_recommended_btn", use_container_width=True):
        st.session_state.view_mode = 'ai_recommendations'
        st.session_state.show_genre_menu = False
        st.rerun()

# Genre dropdown menu (floating overlay style)
if st.session_state.get('show_genre_menu', False):
    # Close button
    close_col1, close_col2, close_col3 = st.columns([2, 1, 2])
    with close_col2:
        if st.button("✕ Close", key="close_menu", use_container_width=True):
            st.session_state.show_genre_menu = False
            st.rerun()
    
    st.markdown("---")
    st.markdown("### 📚 Select Genre")
    
    # Genre grid
    genre_cols = st.columns(4)
    genres = ["All", "Fantasy", "Historical Fiction", "Romance", "Thriller", "Fiction", "Biography", "Children"]
    
    for idx, genre in enumerate(genres):
        with genre_cols[idx % 4]:
            if st.button(f"📖 {genre}", key=f"genre_{genre}", use_container_width=True):
                st.session_state.selected_genre = genre
                st.session_state.view_filter = "All Books"
                st.session_state.show_genre_menu = False
                st.rerun()
    
    st.markdown("---")
    st.markdown("<br><br>", unsafe_allow_html=True)

# Fetch books
try:
    response = requests.get(f"{API_URL}/books")
    if response.status_code == 200:
        all_books = response.json()
        books = all_books.copy()
        
        # ABOUT US MODE
        if st.session_state.view_mode == 'about':
            st.markdown("""
            <div class='about-container'>
                <div class='about-title'>📚 About Our Digital Library</div>
                <div class='about-text'>
                    <p>Welcome to our Digital Library - your gateway to a world of books!</p>
                    
                    🌟 Our library offers a carefully curated collection of books across
                    multiple genres, from timeless classics to contemporary bestsellers.
                    Whether you're looking for thrilling mysteries, heartwarming romances, 
                    or enchanting children's stories, we have something for everyone.
                    
                    📖 Browse our collection, rate your favorite books,
                    save them to your favorites, and create your personal reading list. 
                    Our easy-to-use interface makes discovering your next great read a breeze!
                    
                    🛒 Add books to your cart and place orders for home delivery or 
                    library pickup. Reading has never been more accessible!
                    
                    ✨ Happy Reading! ✨
            </div>
            """, unsafe_allow_html=True)
        
        # GALLERY MODE
        elif st.session_state.view_mode == 'gallery':
            # Filter by search
            if search_query:
                books = [b for b in books if 
                        search_query.lower() in b.get("title", "").lower() or 
                        search_query.lower() in b.get("author", "").lower()]
            
            # Filter by genre
            if st.session_state.selected_genre != "All":
                books = [b for b in books if b.get("genre") == st.session_state.selected_genre]
            
            # Filter by view
            if st.session_state.view_filter == "My Favorites":
                books = [b for b in books if st.session_state.user_id in b.get("favorites", [])]
            elif st.session_state.view_filter == "Top Rated":
                books = [b for b in books if b.get("average_rating", 0) >= 9]
                books = sorted(books, key=lambda x: x.get("average_rating", 0), reverse=True)
            
            # Header
            header_col1, header_col2 = st.columns([3, 1])
            with header_col1:
                filter_name = st.session_state.view_filter
                if st.session_state.selected_genre != "All":
                    filter_name += f" - {st.session_state.selected_genre}"
                st.markdown(f"### 📖 {filter_name}")
            with header_col2:
                st.markdown(f"<p style='text-align: right; color: #888; font-size: 0.85em; margin-top: 10px;'>{len(books)} books</p>", unsafe_allow_html=True)
            
            if books:
                cols_per_row = 5
                for i in range(0, len(books), cols_per_row):
                    if i > 0:
                        st.markdown("<div class='row-separator'></div>", unsafe_allow_html=True)
                    
                    cols = st.columns(cols_per_row)
                    for idx, book in enumerate(books[i:i+cols_per_row]):
                        with cols[idx]:
                            btn_col1, btn_col2, btn_col3, btn_col4 = st.columns([1, 1, 1, 2])
                            
                            with btn_col1:
                                if st.button("🔍", key=f"view_{book['id']}"):
                                    view_book_details(book['id'])
                                    st.rerun()
                            
                            with btn_col2:
                                is_favorite = st.session_state.user_id in book.get("favorites", [])
                                fav_icon = "❤️" if is_favorite else "🤍"
                                if st.button(fav_icon, key=f"fav_{book['id']}"):
                                    requests.post(f"{API_URL}/books/{book['id']}/favorite", 
                                                params={"user_id": st.session_state.user_id})
                                    st.rerun()
                            
                            with btn_col3:
                                is_borrowed = st.session_state.user_id in book.get("borrowed_by", [])
                                cart_icon = "🛒✓" if is_borrowed else "🛒"
                                if st.button(cart_icon, key=f"cart_{book['id']}"):
                                    requests.post(f"{API_URL}/books/{book['id']}/borrow", 
                                                params={"user_id": st.session_state.user_id})
                                    st.rerun()
                            
                            with btn_col4:
                                st.write("")
                            
                            # Use localhost for images - browser can't access 'backend' hostname
                            image_url = book['image_url'].replace('/images/', 'http://localhost:8000/images/')
                            st.markdown(f"""
                            <div class='book-card-container'>
                                <img src='{image_url}' class='book-image'/>
                                <div class='book-title'>{book["title"]}</div>
                                <div class='book-author'>{book["author"]}</div>
                                <div class='book-rating'>⭐ {book.get("average_rating", 0):.1f}/10</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            user_rating = book.get("user_ratings", {}).get(st.session_state.user_id, 0.0)
                            new_rating = st.slider("", 0.0, 10.0, float(user_rating), 0.5, key=f"rate_{book['id']}")
                            
                            if new_rating != user_rating:
                                if st.button("✓ Rate", key=f"submit_{book['id']}"):
                                    requests.post(f"{API_URL}/books/{book['id']}/rate",
                                                params={"user_id": st.session_state.user_id, "rating": new_rating})
                                    st.rerun()
            else:
                st.info("No books found. Try adjusting your filters!")
        
        # DETAILS MODE
        elif st.session_state.view_mode == 'details' and st.session_state.selected_book_id:
            book = next((b for b in all_books if b['id'] == st.session_state.selected_book_id), None)
            
            if book:
                if st.button("← Back to Library"):
                    back_to_gallery()
                    st.rerun()
                
                st.markdown("---")
                st.markdown("## 📖 Book Details")
                
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    image_url = book['image_url'].replace('/images/', 'http://localhost:8000/images/')
                    st.markdown(f"<img src='{image_url}' style='width: 100%; border-radius: 10px;'/>", unsafe_allow_html=True)
                
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
        
        # CART MODE
        elif st.session_state.view_mode == 'cart':
            if st.button("← Back to Library"):
                back_to_gallery()
                st.rerun()
            
            st.markdown("---")
            st.markdown("## 🛒 My Orders")
            
            try:
                cart_response = requests.get(f"{API_URL}/books/cart/{st.session_state.user_id}")
                if cart_response.status_code == 200:
                    cart_books = cart_response.json()
                    
                    if cart_books:
                        st.markdown(f"**You have {len(cart_books)} book(s) ready to borrow**")
                        st.markdown("---")
                        
                        # Display cart books
                        for book in cart_books:
                            col1, col2, col3 = st.columns([1, 3, 1])
                            
                            with col1:
                                image_url = book['image_url'].replace('/images/', 'http://localhost:8000/images/')
                                st.markdown(f"<img src='{image_url}' style='width: 100%; border-radius: 10px;'/>", unsafe_allow_html=True)
                            
                            with col2:
                                st.markdown(f"### {book['title']}")
                                st.markdown(f"**By:** {book['author']}")
                                st.markdown(f"**Genre:** {book['genre']}")
                                st.markdown(f"⭐ {book.get('average_rating', 0):.1f}/10")
                            
                            with col3:
                                if st.button("Remove", key=f"remove_{book['id']}"):
                                    requests.post(f"{API_URL}/books/{book['id']}/borrow",
                                                params={"user_id": st.session_state.user_id})
                                    st.rerun()
                            
                            st.markdown("---")
                        
                        # Checkout button
                        if st.button("📦 Complete Order", use_container_width=True):
                            st.success("🎉 Order completed! Books will be ready for pickup at the library.")
                            st.balloons()
                    else:
                        st.info("Your cart is empty. Browse books and add them to your order!")
                else:
                    st.error("Unable to load cart")
            except Exception as e:
                st.error(f"Error loading cart: {str(e)}")
        
        # WEEKLY RECOMMENDATIONS MODE
        elif st.session_state.view_mode == 'weekly':
            if st.button("← Back to Library"):
                back_to_gallery()
                st.rerun()
            
            st.markdown("---")
            st.markdown("## 🌟 Weekly Top Recommendations")
            st.markdown("*Updated daily by our recommendation system*")
            
            try:
                # Get recommendations from Backend/Redis
                rec_response = requests.get(f"{API_URL}/recommendations/weekly")
                
                if rec_response.status_code == 200:
                    data = rec_response.json()
                    recommendations = data.get("recommendations", [])
                    source = data.get("source", "unknown")
                    
                    # Show source badge
                    if source == "cache":
                        st.success("📦 Loaded from cache (updated daily)")
                    else:
                        st.info("🔄 Loading from database (cache updating in background)")
                    
                    if recommendations:
                        st.markdown("---")
                        
                        # Display recommendations in a nice grid
                        cols = st.columns(min(len(recommendations), 5))
                        
                        for idx, rec in enumerate(recommendations):
                            with cols[idx]:
                                # Find full book data
                                book = next((b for b in all_books if b['id'] == rec['id']), None)
                                
                                if book:
                                    image_url = book['image_url'].replace('/images/', 'http://localhost:8000/images/')
                                    
                                    st.markdown(f"""
                                    <div style='text-align: center; padding: 15px; background: white; 
                                                border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);'>
                                        <img src='{image_url}' style='width: 120px; border-radius: 10px; margin-bottom: 10px;'/>
                                        <p style='font-size: 1em; font-weight: bold; margin: 10px 0 5px 0;'>{book["title"]}</p>
                                        <p style='color: #666; font-size: 0.85em; margin: 5px 0;'>{book["author"]}</p>
                                        <p style='color: #FFD700; font-size: 1.1em; margin: 10px 0;'>⭐ {rec["rating"]:.1f}/10</p>
                                        <p style='color: #888; font-size: 0.8em;'>Based on {rec["total_ratings"]} ratings</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    # View button
                                    if st.button("📖 View", key=f"weekly_view_{rec['id']}", use_container_width=True):
                                        view_book_details(rec['id'])
                                        st.rerun()
                        
                        st.markdown("---")
                        
                        # Refresh button
                        col1, col2, col3 = st.columns([1, 1, 1])
                        with col2:
                            if st.button("🔄 Refresh Recommendations Now", use_container_width=True):
                                refresh_response = requests.post(f"{API_URL}/recommendations/refresh")
                                if refresh_response.status_code == 200:
                                    st.success("✅ Recommendations are being updated! Refresh the page in a few seconds.")
                                else:
                                    st.error("Failed to trigger refresh")
                    else:
                        st.info("No recommendations available yet. Rate some books to get started!")
                else:
                    st.error("Unable to load recommendations")
                    
            except Exception as e:
                st.error(f"Error loading recommendations: {str(e)}")
        # AI RECOMMENDATIONS MODE
        elif st.session_state.view_mode == 'ai_recommendations':
            if st.button("← Back to Library"):
                back_to_gallery()
                st.rerun()
            
            st.markdown("---")
            st.markdown("## 🎯 Recommended for You")
            st.markdown("*Personalized recommendations based on your ratings*")
            
            try:
                # Get AI recommendations
                rec_response = requests.get(f"{API_URL}/recommendations/simple/{st.session_state.user_id}")
                
                if rec_response.status_code == 200:
                    data = rec_response.json()
                    recommendations = data.get("recommendations", [])
                    reasoning = data.get("reasoning", "")
                    
                    if recommendations:
                        st.info(f"💡 {reasoning}")
                        st.markdown("---")
                        
                        # Display recommendations in grid
                        cols = st.columns(min(len(recommendations), 5))
                        
                        for idx, book_data in enumerate(recommendations):
                            with cols[idx]:
                                # Find full book from all_books
                                book = next((b for b in all_books if b['id'] == book_data['id']), None)
                                
                                if book:
                                    image_url = book['image_url'].replace('/images/', 'http://localhost:8000/images/')
                                    
                                    st.markdown(f"""
                                    <div style='text-align: center; padding: 15px; background: white; 
                                                border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                                                border: 2px solid #e91e63;'>
                                        <img src='{image_url}' style='width: 120px; border-radius: 10px; margin-bottom: 10px;'/>
                                        <p style='font-size: 1em; font-weight: bold; margin: 10px 0 5px 0;'>{book["title"]}</p>
                                        <p style='color: #666; font-size: 0.85em; margin: 5px 0;'>{book["author"]}</p>
                                        <p style='color: #FFD700; font-size: 1.1em; margin: 10px 0;'>⭐ {book.get("average_rating", 0):.1f}/10</p>
                                        <p style='color: #e91e63; font-size: 0.85em; margin: 5px 0;'>📚 {book["genre"]}</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    # Action buttons
                                    # Action buttons
                                    btn_cols = st.columns([1, 1, 1])
                                    with btn_cols[0]:
                                        if st.button("🔍", key=f"ai_rec_view_{idx}_{book['id']}"):
                                            view_book_details(book['id'])
                                            st.rerun()
                                    with btn_cols[1]:
                                        is_favorite = st.session_state.user_id in book.get("favorites", [])
                                        if st.button("❤️" if is_favorite else "🤍", key=f"ai_rec_fav_{idx}_{book['id']}"):
                                            requests.post(f"{API_URL}/books/{book['id']}/favorite", 
                                                        params={"user_id": st.session_state.user_id})
                                            st.rerun()
                                    with btn_cols[2]:
                                        is_in_cart = st.session_state.user_id in book.get("borrowed_by", [])
                                        if st.button("🛒✓" if is_in_cart else "🛒", key=f"ai_rec_cart_{idx}_{book['id']}"):
                                            requests.post(f"{API_URL}/books/{book['id']}/borrow",
                                                        params={"user_id": st.session_state.user_id})
                                            st.rerun()
                        
                        st.markdown("---")
                        st.markdown("*💡 Tip: Rate more books to get better recommendations!*")
                    else:
                        st.info("📚 Rate at least 3 books with 7+ stars to get personalized recommendations!")
                        
                        # Show top rated books as fallback
                        top_rated = sorted(all_books, key=lambda x: x.get('average_rating', 0), reverse=True)[:5]
                        st.markdown("### Meanwhile, check out these top-rated books:")
                        
                        cols = st.columns(5)
                        for idx, book in enumerate(top_rated):
                            with cols[idx]:
                                image_url = book['image_url'].replace('/images/', 'http://localhost:8000/images/')
                                st.markdown(f"""
                                <div style='text-align: center; padding: 10px; background: white; border-radius: 10px;'>
                                    <img src='{image_url}' style='width: 100px; border-radius: 8px;'/>
                                    <p style='font-size: 0.9em; margin-top: 8px;'>{book["title"]}</p>
                                    <p style='color: #FFD700;'>⭐ {book["average_rating"]:.1f}</p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                if st.button("View", key=f"fallback_{book['id']}"):
                                    view_book_details(book['id'])
                                    st.rerun()
                else:
                    st.error("Unable to load recommendations")
                    
            except Exception as e:
                st.error(f"Error loading recommendations: {str(e)}")
    else:
        st.error("Failed to load books")
        
except requests.exceptions.ConnectionError:
    st.error("⚠️ Cannot connect to API. Make sure the FastAPI server is running!")