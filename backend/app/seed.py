"""
NestScore seed script — populates the plots table with 50 MUST-area plots.
Idempotent: running twice does not create duplicates.

Run from the backend directory:
    python -m app.seed
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import select
from app.database import AsyncSessionLocal, engine, Base
from app.models.plot import Plot


PLOTS_SEED = [
    # ── Nchiru (22 plots) ──────────────────────────────────────────────────
    {"name": "Karibu Bedsitters", "area": "Nchiru", "gps_lat": -0.0488, "gps_lng": 37.6551,
     "description": "Bedsitter units 0.4km from MUST main gate, shared ablutions, 24hr security, Safaricom fibre in the compound."},
    {"name": "New Life Hostel", "area": "Nchiru", "gps_lat": -0.0502, "gps_lng": 37.6578,
     "description": "Hostel-style accommodation with 4-person rooms, communal kitchen, borehole water, 0.5km from tarmac."},
    {"name": "Green Valley Single Rooms", "area": "Nchiru", "gps_lat": -0.0515, "gps_lng": 37.6534,
     "description": "Self-contained single rooms with private bathrooms, 0.6km from campus. Quiet neighbourhood."},
    {"name": "Phase 4 Plots", "area": "Nchiru", "gps_lat": -0.0465, "gps_lng": 37.6590,
     "description": "Budget bedsitters and double rooms. Water bowser supply. 0.3km to Nchiru stage."},
    {"name": "Corner Plot Nchiru", "area": "Nchiru", "gps_lat": -0.0479, "gps_lng": 37.6612,
     "description": "Corner-situated plot with bedsitter and single room options. Stone construction, iron sheets."},
    {"name": "Sunrise Apartments Nchiru", "area": "Nchiru", "gps_lat": -0.0501, "gps_lng": 37.6620,
     "description": "Newer double rooms with wired electricity and piped water, 0.7km from MUST gate."},
    {"name": "Mwangaza Rentals", "area": "Nchiru", "gps_lat": -0.0525, "gps_lng": 37.6505,
     "description": "Affordable single rooms, shared external bathrooms, reliable water from borehole."},
    {"name": "Bright Future Bedsitters", "area": "Nchiru", "gps_lat": -0.0480, "gps_lng": 37.6498,
     "description": "12-unit plot with bedsitters. Easy matatu access to MUST. Landlord on-site most days."},
    {"name": "Hilltop Nchiru Rooms", "area": "Nchiru", "gps_lat": -0.0471, "gps_lng": 37.6543,
     "description": "Elevated location with good mobile reception. Single rooms, semi-self-contained."},
    {"name": "Mama Pika's Place", "area": "Nchiru", "gps_lat": -0.0537, "gps_lng": 37.6518,
     "description": "Budget option with communal kitchen, 0.8km from campus. Well-known among first-year students."},
    {"name": "Starehe Bedsitters Nchiru", "area": "Nchiru", "gps_lat": -0.0490, "gps_lng": 37.6567,
     "description": "Bedsitters with attached kitchenette. Gated compound. 10-minute walk to MUST library."},
    {"name": "Blue Gate Hostels", "area": "Nchiru", "gps_lat": -0.0508, "gps_lng": 37.6601,
     "description": "Hostel format, 3-person rooms. Common room with TV. Borehole water daily."},
    {"name": "Safari Inn Rooms", "area": "Nchiru", "gps_lat": -0.0522, "gps_lng": 37.6588,
     "description": "Self-contained single rooms and bedsitters. 0.9km from MUST main gate. Near shopping centre."},
    {"name": "Amani Plots Nchiru", "area": "Nchiru", "gps_lat": -0.0463, "gps_lng": 37.6559,
     "description": "Stone-and-cement bedsitters, relatively newer structure, good natural ventilation."},
    {"name": "Tumaini Guest Rooms", "area": "Nchiru", "gps_lat": -0.0533, "gps_lng": 37.6535,
     "description": "Double rooms available. Quiet road. Students report reliable water most months."},
    {"name": "Makao Bora Nchiru", "area": "Nchiru", "gps_lat": -0.0547, "gps_lng": 37.6510,
     "description": "Standard bedsitters 1km from MUST. Shared ablutions, external water storage."},
    {"name": "Furaha Rentals", "area": "Nchiru", "gps_lat": -0.0470, "gps_lng": 37.6530,
     "description": "Mixed bedsitters and single rooms. Walking distance to Nchiru stage."},
    {"name": "Neema Houses Nchiru", "area": "Nchiru", "gps_lat": -0.0495, "gps_lng": 37.6545,
     "description": "Newer 2023 construction, self-contained double rooms. One of the cleaner plots in area."},
    {"name": "Baraka Bedsitters", "area": "Nchiru", "gps_lat": -0.0516, "gps_lng": 37.6570,
     "description": "Bedsitters with shared ablutions. Active WhatsApp group for tenant coordination."},
    {"name": "Jua Kali Rooms Nchiru", "area": "Nchiru", "gps_lat": -0.0483, "gps_lng": 37.6580,
     "description": "Budget-tier plot, water from bowser, iron sheet roofing. Very affordable."},
    {"name": "Zawadi Apartments", "area": "Nchiru", "gps_lat": -0.0509, "gps_lng": 37.6555,
     "description": "Apartment-style single rooms, gated compound, landlord responsive to maintenance."},
    {"name": "Nguvu Hostels Nchiru", "area": "Nchiru", "gps_lat": -0.0527, "gps_lng": 37.6598,
     "description": "4-person hostel rooms near main Nchiru road. Shared kitchen facilities."},

    # ── Katheri (13 plots) ─────────────────────────────────────────────────
    {"name": "Katheri View Bedsitters", "area": "Katheri", "gps_lat": -0.0610, "gps_lng": 37.6510,
     "description": "Bedsitters on the Katheri ridge with good visibility. 1.2km from MUST via tarmac."},
    {"name": "Milima Single Rooms", "area": "Katheri", "gps_lat": -0.0622, "gps_lng": 37.6532,
     "description": "Single rooms on hilly plot, self-contained units, piped water from Katheri scheme."},
    {"name": "Njema Hostels Katheri", "area": "Katheri", "gps_lat": -0.0635, "gps_lng": 37.6545,
     "description": "Hostel-style 3-person rooms. Communal kitchen and common area. 15-minute matatu to MUST."},
    {"name": "Upland Bedsitters Katheri", "area": "Katheri", "gps_lat": -0.0598, "gps_lng": 37.6523,
     "description": "Budget bedsitters on the outskirts of Katheri. Landlord runs a duka on the ground floor."},
    {"name": "Pumzika Rooms Katheri", "area": "Katheri", "gps_lat": -0.0648, "gps_lng": 37.6558,
     "description": "Self-contained double rooms, quiet environment, small garden shared space."},
    {"name": "Green Hill Rentals Katheri", "area": "Katheri", "gps_lat": -0.0612, "gps_lng": 37.6570,
     "description": "Bedsitters and double rooms. Water from commercial tanker twice weekly."},
    {"name": "Mlima Bedsitters", "area": "Katheri", "gps_lat": -0.0625, "gps_lng": 37.6580,
     "description": "Uphill location, cooler climate. 20 units. Known for good landlord relationship."},
    {"name": "Tulia Apartments Katheri", "area": "Katheri", "gps_lat": -0.0638, "gps_lng": 37.6502,
     "description": "Self-contained single rooms with electricity from KPLC, 1.4km from MUST."},
    {"name": "Hope Inn Katheri", "area": "Katheri", "gps_lat": -0.0602, "gps_lng": 37.6541,
     "description": "Mixed hostel and bedsitter format. Longer walk to campus but affordable rent."},
    {"name": "Salama Rooms Katheri", "area": "Katheri", "gps_lat": -0.0659, "gps_lng": 37.6515,
     "description": "12 units, self-contained bedsitters, 1.5km from MUST main gate."},
    {"name": "Uzuri Bedsitters Katheri", "area": "Katheri", "gps_lat": -0.0616, "gps_lng": 37.6560,
     "description": "Cleanly maintained bedsitters with tiled floors. Slightly above average pricing for area."},
    {"name": "Imani Hostels Katheri", "area": "Katheri", "gps_lat": -0.0629, "gps_lng": 37.6535,
     "description": "4-person rooms, freshwater tank on roof, communal study room shared by tenants."},
    {"name": "Bahati Double Rooms Katheri", "area": "Katheri", "gps_lat": -0.0642, "gps_lng": 37.6548,
     "description": "Double rooms for couples or shared occupancy. Good road access from main Katheri route."},

    # ── Campus-adjacent (7 plots) ──────────────────────────────────────────
    {"name": "Gate View Bedsitters", "area": "Campus-adjacent", "gps_lat": -0.0521, "gps_lng": 37.6580,
     "description": "As the name suggests — within sight of MUST main gate. Premium location, priced accordingly."},
    {"name": "Academic Suites", "area": "Campus-adjacent", "gps_lat": -0.0515, "gps_lng": 37.6595,
     "description": "Self-contained single rooms 200m from MUST. The closest plot on the southern end."},
    {"name": "Pioneer Flats", "area": "Campus-adjacent", "gps_lat": -0.0530, "gps_lng": 37.6605,
     "description": "3-storey block, bedsitters and singles. The most popular plot near campus due to proximity."},
    {"name": "Scholar Bedsitters", "area": "Campus-adjacent", "gps_lat": -0.0541, "gps_lng": 37.6572,
     "description": "Bedsitters 350m from MUST. Shared ablutions on each floor. Frequent water supply."},
    {"name": "Campus Edge Rooms", "area": "Campus-adjacent", "gps_lat": -0.0509, "gps_lng": 37.6588,
     "description": "Self-contained units at the edge of the campus buffer zone. Walking time under 5 minutes."},
    {"name": "Tawi Flats", "area": "Campus-adjacent", "gps_lat": -0.0546, "gps_lng": 37.6610,
     "description": "Mixed units: bedsitters, singles, doubles. Landlord lives on-site. Borehole water."},
    {"name": "Summit View Bedsitters", "area": "Campus-adjacent", "gps_lat": -0.0518, "gps_lng": 37.6562,
     "description": "Small 8-unit plot near the back road to MUST. Quiet, good for students who study at home."},

    # ── Other (8 plots) ────────────────────────────────────────────────────
    {"name": "Meru Town Hostel Overflow", "area": "Other", "gps_lat": -0.0472, "gps_lng": 37.6478,
     "description": "Further from campus — 2km+ from MUST. Budget option often used by part-time students."},
    {"name": "Kithangari Bedsitters", "area": "Other", "gps_lat": -0.0558, "gps_lng": 37.6650,
     "description": "Located in Kithangari area, east of campus. Matatu route available. Self-contained units."},
    {"name": "Mikinduri Road Rooms", "area": "Other", "gps_lat": -0.0488, "gps_lng": 37.6640,
     "description": "Along the Mikinduri route. Affordable, 1.8km from MUST. Usually quieter than Nchiru plots."},
    {"name": "Back Village Bedsitters", "area": "Other", "gps_lat": -0.0562, "gps_lng": 37.6478,
     "description": "Rural edge plot west of Nchiru. Very cheap rent, longer walk to campus."},
    {"name": "Kivuli Rooms", "area": "Other", "gps_lat": -0.0475, "gps_lng": 37.6658,
     "description": "Small 6-unit plot by a forested section. Very quiet. Students report poor mobile reception."},
    {"name": "Zawadi Overtime Hostel", "area": "Other", "gps_lat": -0.0550, "gps_lng": 37.6462,
     "description": "Often rented by MUST postgrad and evening-shift students. 2km from main gate."},
    {"name": "Panda Bedsitters", "area": "Other", "gps_lat": -0.0582, "gps_lng": 37.6630,
     "description": "Panda area, slightly south of campus zone. Growing student housing area."},
    {"name": "Ridge Road Single Rooms", "area": "Other", "gps_lat": -0.0465, "gps_lng": 37.6470,
     "description": "Along the ridge road north of MUST. Self-contained singles, cooler altitude location."},
]


async def seed():
    async with AsyncSessionLocal() as db:
        inserted = 0
        skipped = 0
        for data in PLOTS_SEED:
            # Idempotency check by name
            existing = await db.execute(select(Plot).where(Plot.name == data["name"]))
            if existing.scalar_one_or_none():
                skipped += 1
                continue

            plot = Plot(
                name=data["name"],
                area=data["area"],
                description=data["description"],
                gps_lat=data["gps_lat"],
                gps_lng=data["gps_lng"],
            )
            db.add(plot)
            inserted += 1

        await db.commit()
        print(f"Seed complete: {inserted} inserted, {skipped} skipped.")


if __name__ == "__main__":
    asyncio.run(seed())
