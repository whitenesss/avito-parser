import xml.etree.ElementTree as ET

from src.exercise_2.backend.models.ab import Ad


async def parse_xml(file, deduplicator):
    content = await file.read()
    root = ET.fromstring(content)

    stats = {"total": 0, "duplicates": 0, "new": 0, "ads": []}

    for ad_elem in root.findall('ad'):
        ad = Ad(
            title=ad_elem.findtext('title', '').strip(),
            price=ad_elem.findtext('price', '').strip(),
            address=ad_elem.findtext('address', '').strip(),
            link=ad_elem.findtext('link', '').strip()
        )

        stats["total"] += 1

        if deduplicator.is_duplicate(ad):
            stats["duplicates"] += 1
            continue

        deduplicator.add(ad)
        stats["new"] += 1
        stats["ads"].append(ad)

    return stats