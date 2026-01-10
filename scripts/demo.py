#!/usr/bin/env python3
"""
Demo Script for Book Library Project
Demonstrates all main features automatically
"""

import requests
import time
import sys
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

API_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:8501"

def print_header(text):
    """Print a styled header"""
    console.print(Panel(f"[bold cyan]{text}[/bold cyan]", expand=False))

def check_services():
    """Check if all services are running"""
    print_header("🔍 Checking Services")
    
    services = {
        "Backend API": f"{API_URL}/",
        "Frontend": FRONTEND_URL,
    }
    
    all_running = True
    for name, url in services.items():
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                console.print(f"✅ {name}: [green]Running[/green]")
            else:
                console.print(f"❌ {name}: [red]Not responding[/red]")
                all_running = False
        except:
            console.print(f"❌ {name}: [red]Not running[/red]")
            all_running = False
    
    if not all_running:
        console.print("\n[red]❌ Some services are not running![/red]")
        console.print("[yellow]Please run:[/yellow]")
        console.print("  1. docker compose up  (in one terminal)")
        console.print("  2. uv run streamlit run app/streamlit_app.py  (in another terminal)")
        sys.exit(1)
    
    console.print("\n[green]✅ All services are running![/green]\n")

def demo_books_api():
    """Demonstrate books API"""
    print_header("📚 Demo: Books API")
    
    # Get all books
    console.print("Fetching all books...")
    response = requests.get(f"{API_URL}/books")
    books = response.json()
    console.print(f"✅ Found [cyan]{len(books)}[/cyan] books in library\n")
    
    # Show first 3 books
    console.print("[bold]Sample books:[/bold]")
    for book in books[:3]:
        console.print(f"  📖 {book['title']} by {book['author']} ({book['genre']}) - ⭐ {book['average_rating']:.1f}/10")
    
    console.print()
    time.sleep(2)

def demo_user_actions():
    """Demonstrate user actions"""
    print_header("👤 Demo: User Actions")
    
    user_id = "demo_user_123"
    
    # Rate a book
    console.print(f"User [cyan]{user_id}[/cyan] rating 'Harry Potter 1' with 9.5/10...")
    response = requests.post(
        f"{API_URL}/books/1/rate",
        params={"user_id": user_id, "rating": 9.5}
    )
    console.print("✅ Book rated successfully!\n")
    time.sleep(1)
    
    # Add to favorites
    console.print("Adding to favorites...")
    response = requests.post(
        f"{API_URL}/books/1/favorite",
        params={"user_id": user_id}
    )
    console.print("✅ Added to favorites!\n")
    time.sleep(1)
    
    # Add to cart
    console.print("Adding to cart...")
    response = requests.post(
        f"{API_URL}/books/1/borrow",
        params={"user_id": user_id}
    )
    console.print("✅ Added to cart!\n")
    time.sleep(1)
    
    # Check cart
    console.print("Checking cart...")
    response = requests.get(f"{API_URL}/books/cart/{user_id}")
    cart = response.json()
    console.print(f"✅ Cart has [cyan]{len(cart)}[/cyan] book(s)\n")
    time.sleep(2)

def demo_recommendations():
    """Demonstrate recommendations"""
    print_header("🌟 Demo: Weekly Recommendations")
    
    # Get weekly recommendations
    console.print("Fetching weekly top recommendations (from Redis cache)...")
    response = requests.get(f"{API_URL}/recommendations/weekly")
    data = response.json()
    
    source = data.get("source", "unknown")
    recommendations = data.get("recommendations", [])
    
    if source == "cache":
        console.print("✅ Retrieved from [green]Redis cache[/green] (super fast!)\n")
    else:
        console.print("✅ Retrieved from [yellow]database[/yellow] (cache updating...)\n")
    
    console.print(f"[bold]Top {len(recommendations)} recommended books:[/bold]")
    for i, book in enumerate(recommendations, 1):
        console.print(f"  {i}. {book['title']} by {book['author']} - ⭐ {book['rating']:.1f}/10")
    
    console.print()
    time.sleep(2)

def demo_ai_recommendations():
    """Demonstrate AI recommendations"""
    print_header("�� Demo: AI-Powered Recommendations")
    
    user_id = "demo_user_123"
    
    console.print(f"Getting personalized recommendations for user [cyan]{user_id}[/cyan]...")
    response = requests.get(f"{API_URL}/recommendations/simple/{user_id}")
    data = response.json()
    
    recommendations = data.get("recommendations", [])
    reasoning = data.get("reasoning", "")
    
    console.print(f"✅ {reasoning}\n")
    
    if recommendations:
        console.print("[bold]Personalized recommendations:[/bold]")
        for i, book in enumerate(recommendations[:5], 1):
            console.print(f"  {i}. {book['title']} by {book['author']} ({book['genre']}) - ⭐ {book['average_rating']:.1f}/10")
    else:
        console.print("[yellow]Rate more books to get personalized recommendations![/yellow]")
    
    console.print()
    time.sleep(2)

def demo_background_worker():
    """Demonstrate background worker"""
    print_header("⚙️ Demo: Background Worker")
    
    console.print("Triggering manual recommendation refresh (background task)...")
    response = requests.post(f"{API_URL}/recommendations/refresh")
    data = response.json()
    
    task_id = data.get("task_id")
    console.print(f"✅ Task created: [cyan]{task_id}[/cyan]\n")
    
    console.print("Checking task status...")
    time.sleep(2)
    
    response = requests.get(f"{API_URL}/tasks/{task_id}")
    task_data = response.json()
    
    status = task_data.get("status")
    console.print(f"Task status: [cyan]{status}[/cyan]\n")
    time.sleep(2)

def main():
    """Main demo function"""
    console.print("\n")
    console.print(Panel.fit(
        "[bold magenta]�� Book Library - Full Demo[/bold magenta]\n"
        "[cyan]Demonstrating all features automatically[/cyan]",
        border_style="magenta"
    ))
    console.print("\n")
    
    try:
        # Check services
        check_services()
        
        # Run demos
        demo_books_api()
        demo_user_actions()
        demo_recommendations()
        demo_ai_recommendations()
        demo_background_worker()
        
        # Summary
        print_header("✅ Demo Complete!")
        console.print("[green]All features demonstrated successfully![/green]\n")
        console.print("🌐 Visit the frontend at: [cyan]http://localhost:8501[/cyan]")
        console.print("📖 API docs at: [cyan]http://localhost:8000/docs[/cyan]\n")
        
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Demo interrupted by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Error: {str(e)}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()
