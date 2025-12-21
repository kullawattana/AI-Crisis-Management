"""
Fix existing victim data:
1. Add ticket numbers to records without them
2. Fix timezone offset (subtract 7 hours from timestamps that were incorrectly saved as local time)
"""
from google.cloud import firestore
from datetime import datetime, timedelta, timezone
import random

db = firestore.Client()

def generate_ticket_number(created_at: datetime) -> str:
    """Generate ticket number based on creation date."""
    year = created_at.year
    month = str(created_at.month).zfill(2)
    day = str(created_at.day).zfill(2)
    seq = str(random.randint(0, 999999)).zfill(6)
    return f"C{year}{month}{day}{seq}"


def needs_timezone_fix(ts) -> bool:
    """Check if timestamp is in the future (indicating wrong timezone)."""
    if ts is None:
        return False
    now = datetime.now(timezone.utc)
    # If timestamp is more than 1 hour in the future, it's likely wrong
    return (ts - now).total_seconds() > 3600


def main():
    print("Fetching victims...")
    print(f"Current UTC: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    victims_ref = db.collection('victims')
    victims = list(victims_ref.stream())

    fixed_count = 0
    tz_fixed = 0

    for victim in victims:
        data = victim.to_dict()
        updates = {}

        created_at = data.get('createdAt')

        # Check if this record needs timezone fix (createdAt is in the future)
        if created_at and needs_timezone_fix(created_at):
            print(f"\n{victim.id} needs timezone fix (created: {created_at.strftime('%H:%M')} UTC)")

            # Fix all timestamp fields by subtracting 7 hours
            timestamp_fields = ['createdAt', 'updatedAt', 'lastContactAt', 'nextPulseAt', 'callbackDueAt']

            for field in timestamp_fields:
                ts = data.get(field)
                if ts:
                    fixed_ts = ts - timedelta(hours=7)
                    updates[field] = fixed_ts
                    print(f"  {field}: {ts.strftime('%H:%M')} -> {fixed_ts.strftime('%H:%M')}")

            tz_fixed += 1

        # Add assignedResources if missing
        if 'assignedResources' not in data:
            updates['assignedResources'] = []

        if updates:
            victims_ref.document(victim.id).update(updates)
            fixed_count += 1

    print(f"\nDone! Updated {fixed_count} records, fixed timezone on {tz_fixed} records.")


if __name__ == '__main__':
    main()
