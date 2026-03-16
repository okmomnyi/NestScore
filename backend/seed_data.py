"""
Data seeding script for NestScore database.
Collects real rental plot data from Google Maps and other sources.
"""
import asyncio
import os
import sys
from datetime import datetime
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.dirname(__file__))

from app.models.plot import Plot
from app.models.review import Review
from app.config import settings


GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")

RENTAL_AREAS = [
    {"name": "Nchiru", "lat": -0.0530, "lng": 37.6560},
    {"name": "Katheri", "lat": -0.0580, "lng": 37.6480},
    {"name": "Campus-adjacent", "lat": -0.0490, "lng": 37.6620},
]

SAMPLE_PLOTS = [
    {
        "name": "Amerukan Residency",
        "area": "Nchiru",
        "description": "Popular student housing near Meru University with modern amenities and good security.",
        "gps_lat": -0.0532,
        "gps_lng": 37.6558,
    },
    {
        "name": "Katheri Hostels",
        "area": "Katheri",
        "description": "Affordable accommodation with easy access to campus and local markets.",
        "gps_lat": -0.0578,
        "gps_lng": 37.6482,
    },
    {
        "name": "Campus View Apartments",
        "area": "Campus-adjacent",
        "description": "Premium student apartments with Wi-Fi, water, and 24/7 security.",
        "gps_lat": -0.0492,
        "gps_lng": 37.6618,
    },
    {
        "name": "Nchiru Plaza",
        "area": "Nchiru",
        "description": "Centrally located with shops and restaurants nearby. Good transport links.",
        "gps_lat": -0.0528,
        "gps_lng": 37.6565,
    },
    {
        "name": "Green Valley Hostels",
        "area": "Katheri",
        "description": "Quiet neighborhood with spacious rooms and reliable utilities.",
        "gps_lat": -0.0582,
        "gps_lng": 37.6475,
    },
    {
        "name": "University Heights",
        "area": "Campus-adjacent",
        "description": "Walking distance to campus with study rooms and common areas.",
        "gps_lat": -0.0488,
        "gps_lng": 37.6625,
    },
    {
        "name": "Meru Student Lodge",
        "area": "Nchiru",
        "description": "Budget-friendly option with basic amenities and friendly landlord.",
        "gps_lat": -0.0535,
        "gps_lng": 37.6552,
    },
    {
        "name": "Katheri Gardens",
        "area": "Katheri",
        "description": "Well-maintained compound with parking and laundry facilities.",
        "gps_lat": -0.0575,
        "gps_lng": 37.6488,
    },
    {
        "name": "Campus Gate Residency",
        "area": "Campus-adjacent",
        "description": "Right next to main gate, perfect for students who value convenience.",
        "gps_lat": -0.0495,
        "gps_lng": 37.6615,
    },
    {
        "name": "Nchiru Central",
        "area": "Nchiru",
        "description": "Mixed use building with shops on ground floor and rooms above.",
        "gps_lat": -0.0525,
        "gps_lng": 37.6570,
    },
]

SAMPLE_REVIEWS = [
    {
        "plot_name": "Amerukan Residency",
        "rating": 4.5,
        "comment": "Great location and the landlord is very responsive. Water is always available.",
    },
    {
        "plot_name": "Amerukan Residency",
        "rating": 3.5,
        "comment": "Good place but can get noisy during weekends. Otherwise decent.",
    },
    {
        "plot_name": "Katheri Hostels",
        "rating": 4.0,
        "comment": "Affordable and close to everything. Rooms are clean and spacious.",
    },
    {
        "plot_name": "Campus View Apartments",
        "rating": 5.0,
        "comment": "Best place I've stayed! Fast Wi-Fi, hot water, and great security.",
    },
    {
        "plot_name": "Campus View Apartments",
        "rating": 4.0,
        "comment": "A bit pricey but worth it for the amenities and location.",
    },
    {
        "plot_name": "Nchiru Plaza",
        "rating": 3.0,
        "comment": "Convenient location but maintenance could be better. Water issues sometimes.",
    },
    {
        "plot_name": "Green Valley Hostels",
        "rating": 4.5,
        "comment": "Quiet and peaceful. Perfect for serious students. Landlady is kind.",
    },
    {
        "plot_name": "University Heights",
        "rating": 4.0,
        "comment": "Walking to class is so easy. Study rooms are a nice touch.",
    },
    {
        "plot_name": "Meru Student Lodge",
        "rating": 3.5,
        "comment": "Basic but affordable. Good for students on a tight budget.",
    },
    {
        "plot_name": "Katheri Gardens",
        "rating": 4.5,
        "comment": "Well maintained compound. Parking is a big plus. Highly recommend.",
    },
]


async def search_google_places(area_name: str, lat: float, lng: float):
    """Search for rental properties using Google Places API."""
    if not GOOGLE_MAPS_API_KEY:
        print(f"Skipping Google Places search for {area_name} (no API key)")
        return []
    
    try:
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            "location": f"{lat},{lng}",
            "radius": 1500,
            "keyword": "student hostel OR rental apartment OR student accommodation",
            "key": GOOGLE_MAPS_API_KEY,
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for place in data.get("results", [])[:5]:
                    results.append({
                        "name": place.get("name"),
                        "area": area_name,
                        "description": f"Located in {area_name}. {place.get('vicinity', '')}",
                        "gps_lat": place["geometry"]["location"]["lat"],
                        "gps_lng": place["geometry"]["location"]["lng"],
                    })
                
                print(f"Found {len(results)} places from Google Maps in {area_name}")
                return results
            else:
                print(f"Google Places API error: {response.status_code}")
                return []
    except Exception as e:
        print(f"Error searching Google Places: {e}")
        return []


async def seed_database():
    """Seed the database with rental plot data."""
    print("Starting database seeding...")
    
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            existing_plots = await session.execute(select(Plot))
            existing_count = len(existing_plots.scalars().all())
            
            if existing_count > 0:
                print(f"\nDatabase already has {existing_count} plots.")
                response = input("Do you want to clear existing data and reseed? (yes/no): ")
                if response.lower() == "yes":
                    await session.execute(Review.__table__.delete())
                    await session.execute(Plot.__table__.delete())
                    await session.commit()
                    print("Cleared existing data.")
                else:
                    print("Keeping existing data. Adding new plots only.")
            
            all_plots = []
            
            print("\n1. Adding sample plots...")
            all_plots.extend(SAMPLE_PLOTS)
            
            print("\n2. Searching Google Maps for additional plots...")
            for area in RENTAL_AREAS:
                google_plots = await search_google_places(
                    area["name"], area["lat"], area["lng"]
                )
                all_plots.extend(google_plots)
            
            print(f"\n3. Inserting {len(all_plots)} plots into database...")
            plot_map = {}
            
            for plot_data in all_plots:
                existing = await session.execute(
                    select(Plot).where(Plot.name == plot_data["name"])
                )
                if existing.scalar_one_or_none():
                    print(f"  - Skipping duplicate: {plot_data['name']}")
                    continue
                
                plot = Plot(
                    name=plot_data["name"],
                    area=plot_data["area"],
                    description=plot_data["description"],
                    gps_lat=plot_data["gps_lat"],
                    gps_lng=plot_data["gps_lng"],
                    status="active",
                    weighted_score=0.0,
                    total_ratings=0,
                )
                session.add(plot)
                plot_map[plot_data["name"]] = plot
                print(f"  + Added: {plot_data['name']}")
            
            await session.commit()
            
            print("\n4. Adding sample reviews...")
            for review_data in SAMPLE_REVIEWS:
                plot_name = review_data["plot_name"]
                if plot_name not in plot_map:
                    result = await session.execute(
                        select(Plot).where(Plot.name == plot_name)
                    )
                    plot = result.scalar_one_or_none()
                    if not plot:
                        continue
                else:
                    plot = plot_map[plot_name]
                
                review = Review(
                    plot_id=plot.id,
                    rating_overall=review_data["rating"],
                    comment_text=review_data["comment"],
                    status="active",
                    fingerprint_hash=f"seed_{plot_name}_{review_data['rating']}",
                )
                session.add(review)
                print(f"  + Added review for: {plot_name}")
            
            await session.commit()
            
            print("\n5. Calculating initial scores...")
            plots_result = await session.execute(select(Plot))
            for plot in plots_result.scalars().all():
                reviews_result = await session.execute(
                    select(Review).where(
                        Review.plot_id == plot.id,
                        Review.status == "active"
                    )
                )
                reviews = reviews_result.scalars().all()
                
                if reviews:
                    avg_score = sum(r.rating_overall for r in reviews) / len(reviews)
                    plot.weighted_score = avg_score
                    plot.total_ratings = len(reviews)
            
            await session.commit()
            
            final_plots = await session.execute(select(Plot))
            final_reviews = await session.execute(select(Review))
            
            print("\n" + "="*60)
            print("DATABASE SEEDING COMPLETE!")
            print("="*60)
            print(f"Total Plots: {len(final_plots.scalars().all())}")
            print(f"Total Reviews: {len(final_reviews.scalars().all())}")
            print("\nYou can now start the application and view the data!")
            print("="*60)
            
        except Exception as e:
            print(f"\nError during seeding: {e}")
            await session.rollback()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_database())
