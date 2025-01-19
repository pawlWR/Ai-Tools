from django.db import transaction
from typing import Any, List, Tuple

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import Checkpoint, CheckpointMetadata, CheckpointTuple,BaseCheckpointSaver

from .models import Checkpoint

class DjangoSaver(BaseCheckpointSaver):
    def get_tuple(self, config: RunnableConfig) -> CheckpointTuple | None:
        thread_id = config["configurable"]["thread_id"]
        thread_ts = config["configurable"].get("thread_ts")

        if thread_ts:
            checkpoint_obj = (
                Checkpoint.objects.filter(thread_id=thread_id, checkpoint_id=thread_ts)
                .values_list("checkpoint", "metadata", "checkpoint_id", "parent_checkpoint_id")
                .first()
            )
        else:
            checkpoint_obj = (
                Checkpoint.objects.filter(thread_id=thread_id)
                .order_by("-checkpoint_id")
                .values_list("checkpoint", "metadata", "checkpoint_id", "parent_checkpoint_id")
                .first()
            )

        if checkpoint_obj:
            checkpoint, metadata, checkpoint_id, parent_checkpoint_id = checkpoint_obj
            if not config["configurable"].get("thread_ts"):
                config = {
                    "configurable": {
                        "thread_id": thread_id,
                        "thread_ts": checkpoint_id,
                    }
                }

            return CheckpointTuple(
                config=config,
                checkpoint=self.serde.loads(checkpoint) if checkpoint else None,
                metadata=self.serde.loads(metadata) if metadata else None,
                parent_config=(
                    {
                        "configurable": {
                            "thread_id": thread_id,
                            "thread_ts": parent_checkpoint_id,
                        }
                    }
                    if parent_checkpoint_id
                    else None
                ),
                pending_writes=[],  # Modify if pending writes are required
            )

    def put(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        *args,  # Adding *args to capture any additional arguments passed
        **kwargs  # Optional: to capture keyword arguments
    ) -> RunnableConfig:
        thread_id = config["configurable"]["thread_id"]
        checkpoint_id = checkpoint["id"]
        parent_checkpoint_id = config["configurable"].get("thread_ts")

        Checkpoint.objects.update_or_create(
            checkpoint_id=checkpoint_id,
            defaults={
                "thread_id": thread_id,
                "checkpoint_ns": config.get("namespace", ""),
                "parent_checkpoint_id": parent_checkpoint_id,
                "type": checkpoint.get("type", ""),
                "checkpoint": self.serde.dumps(checkpoint) if checkpoint else None,
                "metadata": self.serde.dumps(metadata) if metadata else None,
            },
        )
        return config

    def put_writes(
        self, config: RunnableConfig, writes: List[Tuple[str, Any]], task_id: str
    ) -> None:
        pass  # Implement if needed based on writes behavior
