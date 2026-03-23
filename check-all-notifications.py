"""
Check all notifications and their ticket IDs
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv('production/.env')

async def check_notifications():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    
    # Get all notifications with their URLs
    notifs = await conn.fetch("""
        SELECT id, url, reference_id, metadata, created_at 
        FROM notifications 
        ORDER BY created_at DESC 
        LIMIT 20
    """)
    
    print("Current notifications:")
    print("=" * 80)
    
    for n in notifs:
        url = n['url'] or 'N/A'
        ref_id = n['reference_id'] or 'N/A'
        metadata = n['metadata'] or {}
        ticket_id_meta = metadata.get('ticket_id', 'N/A') if isinstance(metadata, dict) else 'N/A'
        created = n['created_at'].strftime('%Y-%m-%d %H:%M') if n['created_at'] else 'N/A'
        
        print(f"Created: {created}")
        print(f"  URL: {url}")
        print(f"  Reference ID: {ref_id}")
        print(f"  Metadata ticket_id: {ticket_id_meta}")
        print("-" * 80)
    
    # Check for mismatched IDs
    print("\n\n🔍 Checking for ID mismatches...")
    print("=" * 80)
    
    mismatches = []
    for n in notifs:
        url = n['url'] or ''
        ref_id = n['reference_id'] or ''
        metadata = n['metadata'] or {}
        ticket_id_meta = metadata.get('ticket_id', '') if isinstance(metadata, dict) else ''
        
        # Extract ticket ID from URL
        if '/TKT-' in url:
            url_ticket_id = url.split('/TKT-')[1].split('/')[0] if '/TKT-' in url else ''
        else:
            url_ticket_id = ''
        
        # Check if IDs match
        if url_ticket_id and ref_id and url_ticket_id != ref_id:
            mismatches.append({
                'url_id': url_ticket_id,
                'ref_id': ref_id,
                'meta_id': ticket_id_meta,
                'url': url
            })
    
    if mismatches:
        print(f"Found {len(mismatches)} mismatches:")
        for m in mismatches:
            print(f"  ❌ URL: TKT-{m['url_id']} | Ref: {m['ref_id']} | Meta: {m['meta_id']}")
    else:
        print("✅ All IDs match!")
    
    await conn.close()

asyncio.run(check_notifications())
