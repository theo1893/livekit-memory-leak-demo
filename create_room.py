import asyncio

from config import LIVEKIT_URL, LIVEKIT_KEY, LIVEKIT_SECRET
from livekit_service import LiveKitManager


async def main() -> None:
    manager = LiveKitManager(LIVEKIT_URL, LIVEKIT_KEY, LIVEKIT_SECRET)

    room_name = await manager.create_room(metadata='{}', empty_timeout=30)
    url, token = manager.generate_token(room_name=room_name, identity="user", participator_name="test",
                                        participant_meta="{}")
    print(f"url = {url} \n" + f"token = {token} \n \n" + f"room_name = {room_name}")


if __name__ == "__main__":
    asyncio.run(main())
