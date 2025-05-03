import time
import uuid
from typing import Optional

from livekit import api
from livekit.api import CreateRoomRequest, LiveKitAPI


class LiveKitManager:
    lkapi: Optional[LiveKitAPI]
    url: str = ""
    api_key: str = ""
    api_secret: str = ""

    def __init__(self, url: str, api_key: str, api_secret: str):
        self.lkapi = LiveKitAPI(url=url, api_key=api_key, api_secret=api_secret)
        self.url = url
        self.api_key = api_key
        self.api_secret = api_secret

    def close(self):
        # TODO
        self.lkapi.aclose()

    def generate_token(self, room_name, identity, participator_name, participant_meta):
        token = (
            api.AccessToken(self.api_key, self.api_secret)
            .with_identity(identity)
            .with_name(participator_name)
            .with_grants(
                api.VideoGrants(
                    room_join=True,
                    room=room_name,
                )
            ).with_metadata(participant_meta)
        )
        token = token.to_jwt()
        return (self.url, token)

    def get_random_id(self) -> str:
        timestamp = int(time.time() * 1000)
        id = str(uuid.uuid1(clock_seq=timestamp))
        return id

    async def create_room(
            self,
            metadata: str,
            empty_timeout: int = 10 * 60,
            max_participants: int = 20,
    ) -> str:
        room_name = f"s:user:{self.get_random_id()}"

        await self.lkapi.room.create_room(
            CreateRoomRequest(
                name=room_name, empty_timeout=empty_timeout, max_participants=max_participants, metadata=metadata
            )
        )
        return room_name
