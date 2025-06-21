from django.core.management.base import BaseCommand
from Transportation.models import BusSchedule

bus_schedule_data = [
    ("6:30", "Patna (Bihar Museum)", "IIT"),
    ("7:45", "Kalam", "Tut Block"),
    ("7:55", "Kalam", "Tut Block"),
    ("8:45", "Kalam", "Tutblock"),
    ("8:55", "Kalam", "Tutblock"),
    ("9:05", "Kalam", "Tutblock"),
    ("9:50", "Kalam", "Tut Block"),
    ("10:10", "Tut Block", "Kalam"),
    ("10:50", "Kalam", "Tut Block"),
    ("11:10", "Tut Block", "Kalam"),
    ("11:50", "Kalam", "Tut Block"),
    ("12:05", "Tut Block", "Kalam"),
    ("12:15", "Tut Block", "Kalam"),
    ("13:05", "Tut Block", "Kalam"),
    ("13:15", "Tut Block", "Kalam"),
    ("13:25", "Tut Block", "Kalam"),
    ("13:45", "Kalam", "Tut Block"),
    ("13:55", "Kalam", "Tut Block"),
    ("14:05", "Kalam", "Tutblock"),
    ("14:10", "Tut Block", "Kalam"),
    ("14:50", "Kalam", "Tut Block"),
    ("15:10", "Tut Block", "Kalam"),
    ("15:50", "Kalam", "Tut Block"),
    ("16:10", "Tut Block", "Kalam"),
    ("16:50", "Kalam", "Tutblock"),
    ("17:05", "Tut Block", "Kalam"),
    ("17:15", "IIT", "Patna (Bihar Museum)"),
]

from datetime import datetime, timedelta

def add_15_minutes(time_str):
    try:
        t = datetime.strptime(time_str.strip(), "%H:%M")
    except ValueError:
        t = datetime.strptime(time_str.strip(), "%H:%M%p")  # fallback
    t_plus_15 = t + timedelta(minutes=15)
    return t_plus_15.strftime("%H:%M")

class Command(BaseCommand):
    help = 'Seed bus schedule data with frequency 15 mins'

    def handle(self, *args, **options):
        for departure_time, from_loc, to_loc in bus_schedule_data:
            arrival_time = add_15_minutes(departure_time)
            BusSchedule.objects.create(
                bus_name=f"{from_loc} to {to_loc}",
                from_location=from_loc,
                to_location=to_loc,
                departure_time=departure_time,
                arrival_time=arrival_time,
                frequency="Every 15 min"
            )
        self.stdout.write(self.style.SUCCESS("✅ Bus schedule data seeded successfully!"))
