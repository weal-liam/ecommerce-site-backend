import logging
import time

logger = logging.getLogger(__name__)


class RequestResponseLoggingMiddleware:
    """Middleware that logs basic request and response information.

    - Logs method, path, user, truncated request body (first 1000 chars).
    - Logs response status and truncated body and duration in ms.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger(__name__)

    def __call__(self, request):
        start = time.time()
        # Attempt to read request body safely (may be large / binary)
        try:
            body = request.body.decode('utf-8') if hasattr(request, 'body') and request.body else ''
        except Exception:
            body = '<unreadable>'

        user = getattr(request, 'user', None)
        self.logger.info(
            'Request start: method=%s path=%s user=%s body=%s',
            request.method,
            request.get_full_path(),
            user,
            (body[:1000] + '...') if len(body) > 1000 else body,
        )

        response = self.get_response(request)

        duration_ms = (time.time() - start) * 1000
        try:
            resp_body = response.content.decode('utf-8') if hasattr(response, 'content') and response.content else ''
        except Exception:
            resp_body = '<unreadable>'

        self.logger.info(
            'Request end: status=%s path=%s duration_ms=%.2f response_body=%s',
            getattr(response, 'status_code', 'unknown'),
            request.get_full_path(),
            duration_ms,
            (resp_body[:1000] + '...') if len(resp_body) > 1000 else resp_body,
        )

        return response
