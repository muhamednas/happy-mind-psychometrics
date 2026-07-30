import random
import string
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.package import Package

async def generate_access_code(session: AsyncSession) -> str:
    """Generate HM-XXXX-X codes where XXXX = 4 uppercase alphanumeric chars, X = 1 check digit."""
    while True:
        chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        check_digit = str(sum(ord(c) for c in chars) % 10)
        code = f"HM-{chars}-{check_digit}"
        
        result = await session.execute(select(Package).where(Package.access_code == code))
        if not result.scalars().first():
            return code
