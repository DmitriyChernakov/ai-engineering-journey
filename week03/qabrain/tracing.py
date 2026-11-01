import base64

from langfuse import get_client
from openinference.instrumentation.llama_index import LlamaIndexInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

from config import LANGFUSE_BASE_URL, LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY

_auth = base64.b64encode(
    f"{LANGFUSE_PUBLIC_KEY}:{LANGFUSE_SECRET_KEY}".encode("utf-8")
).decode("ascii")


def setup_tracing() -> None:
    tracer_provider = TracerProvider()
    tracer_provider.add_span_processor(
        SimpleSpanProcessor(
            OTLPSpanExporter(
                endpoint=f"{LANGFUSE_BASE_URL}/api/public/otel/v1/traces",
                headers={
                    "Authorization": f"Basic {_auth}",
                    "x-langfuse-ingestion-version": "4",
                },
            )
        )
    )

    LlamaIndexInstrumentor().instrument(tracer_provider=tracer_provider)
