from celery import Celery
from kombu import Queue
from app.config import settings

celery_app = Celery(
    "qp_search",
    broker=settings.celery_broker_url,
    backend=settings.celery_broker_url,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
    task_soft_time_limit=3000,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    imports=[
        "app.tasks.pdf_processor",
        "app.tasks.datalab_processor",
    ],
    # Define task queues
    task_queues=(
        Queue("celery", routing_key="celery"),  # Default queue for LlamaCloud tasks
        Queue("datalab", routing_key="datalab"),  # Separate queue for datalab tasks
    ),
    task_default_queue="celery",
    task_default_routing_key="celery",
    # Route datalab tasks to datalab queue
    task_routes={
        "process_datalab_pdf_task": {"queue": "datalab"},
    },
)
