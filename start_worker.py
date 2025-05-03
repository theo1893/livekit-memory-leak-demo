import asyncio
import psutil
import os

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions, JobExecutorType, AutoSubscribe
from livekit.agents import Worker, WorkerOptions
from livekit.agents.ipc.job_executor import JobExecutor
from livekit.plugins import (
    openai,
    deepgram,
    noise_cancellation,
)
from loguru import logger

from config import DEEPGRAM_KEY, OPENAI_KEY, LIVEKIT_URL, LIVEKIT_KEY, LIVEKIT_SECRET
from utils import plt_rss


async def entrypoint(job_ctx: agents.JobContext):
    ## TODO TEST
    @job_ctx.room.on("participant_connected")
    def participant_connected():
        print("[ROOM] participant connected")

    @job_ctx.room.on("participant_disconnected")
    def participant_disconnected():
        print("[ROOM] participant disconnected")

    @job_ctx.room.on("local_track_published")
    def local_track_published():
        print("[ROOM] local track published")

    @job_ctx.room.on("local_track_subscribed")
    def local_track_subscribed():
        print("[ROOM] local track subscribed")

    @job_ctx.room.on("local_track_unpublished")
    def local_track_unpublished():
        print("[ROOM] local track unpublished")

    @job_ctx.room.on("track_published")
    def track_published():
        print("[ROOM] track published")

    @job_ctx.room.on("track_subscribed")
    def track_subscribed():
        print("[ROOM] track subscribed")

    @job_ctx.room.on("track_unsubscribed")
    def track_unsubscribed():
        print("[ROOM] track unsubscribed")

    @job_ctx.room.on("track_muted")
    def track_muted():
        print("[ROOM] track muted")

    @job_ctx.room.on("track_unmuted")
    def track_unmuted():
        print("[ROOM] track unmuted")

    @job_ctx.room.on("active_speakers_changed")
    def active_speaker_changed():
        print("[ROOM] active speakers changed")

    @job_ctx.room.on("room_metadata_changed")
    def room_metadata_changed():
        print("[ROOM] room metadata changed")

    @job_ctx.room.on("participant_name_changed")
    def participant_name_changed():
        print("[ROOM] participant name changed")

    @job_ctx.room.on("transcription_received")
    def transcription_received():
        print("[ROOM] transcription received")

    @job_ctx.room.on("e2ee_state_changed")
    def e2ee_state_changed(identity: str, status):
        print(f"[ROOM] e2ee state changed, id={identity}, status={status}")

    @job_ctx.room.on("connection_state_changed")
    def connection_state_changed(status):
        print(f"[ROOM] connection state changed, status={status}")

    @job_ctx.room.on("connected")
    def connected():
        print("[ROOM] connected")

    @job_ctx.room.on("disconnected")
    def disconnected():
        print("[ROOM] disconnected")

    @job_ctx.room.on("reconnecting")
    def reconnecting():
        print("[ROOM] reconnecting")

    @job_ctx.room.on("reconnected")
    def reconnected():
        print("[ROOM] reconnected")

    await job_ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # participant = await job_ctx.wait_for_participant()
    # logger.info(f"starting copilot for participant {participant.identity}")

    logger.info(f"connecting to room {job_ctx.room.name}")

    session = AgentSession(
        stt=deepgram.STT(model="nova-3", api_key=DEEPGRAM_KEY),
        llm=openai.LLM(model="gpt-4o-mini", api_key=OPENAI_KEY),
        tts=openai.TTS(api_key=OPENAI_KEY),
    )

    async def clear_work() -> None:
        await session.drain()
        await session.aclose()

    job_ctx.add_shutdown_callback(clear_work)

    await session.start(
        room=job_ctx.room,
        agent=Agent(
            instructions="You are a helpful assistant",
        ),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )


## This func is used to record memory usage
async def log_memory_usage():
    count_limit = 600
    count = 1
    rss_data = []
    process = psutil.Process(os.getpid())

    while True:
        await asyncio.sleep(1)

        cur_mem = process.memory_info()
        print(
            f"[Memory] Mem : RSS={cur_mem.rss / (1024 * 1024):.2f} MB, VMS={cur_mem.vms / (1024 * 1024):.2f} MB, Pid={process.pid}")
        rss_data.append(cur_mem.rss / (1024 * 1024))

        count = count + 1
        if count >= count_limit:
            plt_rss(rss_data)
            print("Plt is done. You can quit now.")
            return

def main() -> None:
    worker = Worker(
        opts=WorkerOptions(
            entrypoint_fnc=entrypoint,
            ws_url=LIVEKIT_URL,
            api_key=LIVEKIT_KEY,
            api_secret=LIVEKIT_SECRET,
            port=11112,
            initialize_process_timeout=10,
            job_executor_type=JobExecutorType.THREAD,
        ),
        devmode=False,
        loop=asyncio.get_event_loop(),
    )

    @worker._proc_pool.on("process_job_launched")
    def process_job_launched(job: JobExecutor):
        print(f"[Process Job] process job launched")

    @worker._proc_pool.on("process_created")
    def process_job_created(job: JobExecutor):
        print(f"[Process] process created")

    @worker._proc_pool.on("process_started")
    def process_job_started(job: JobExecutor):
        print(f"[Process] process started")

    @worker._proc_pool.on("process_ready")
    def process_job_ready(job: JobExecutor):
        print(f"[Process] process ready")

    @worker._proc_pool.on("process_closed")
    def process_job_closed(job: JobExecutor):
        print(f"[Process] process closed")

    loop = asyncio.get_event_loop()
    task1 = loop.create_task(worker.run())
    task2 = loop.create_task(log_memory_usage())
    loop.run_until_complete(asyncio.gather(task1, task2))

if __name__ == "__main__":
    main()