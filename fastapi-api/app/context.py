from contextvars import ContextVar

trace_id_ctx = ContextVar("trace_id", default="")


def set_trace_id(trace_id: str = ""):
    return trace_id_ctx.set(trace_id)


def get_trace_id():
    return trace_id_ctx.get()


def set_request_context_var(**kwargs):
    trace_id = kwargs.get("trace_id", "")
    set_trace_id(trace_id)
