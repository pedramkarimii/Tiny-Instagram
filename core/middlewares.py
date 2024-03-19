import logging
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse

"""Initialize the logger with the current module name."""
logger = logging.getLogger(__name__)

"""Define the path for the log file."""
LOG_FILE_PATH = '/home/pedram/Desktop/project django/core/info.log'

"""Configure logging with the specified log file, log level, and format."""
logging.basicConfig(filename=LOG_FILE_PATH, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class LoginRequiredMiddleware:
    """Middleware class to handle login requirement."""

    def __init__(self, get_response):
        """Initialize the middleware."""
        self.get_response = get_response

    def __call__(self, request):
        """Handle each incoming request."""

        logger.info(f"Request for URL: {request.path}. Method: {request.method}.")

        response = self.get_response(request)

        if response.status_code in [400, 404, 405, 406, 500, 401, 403]:
            logger.error(
                f"Error {response.status_code} occurred for URL: {request.path}. "
                f"Method: {request.method}. User: {request.user}")
            messages.warning(request, 'An error occurred. Please try again.', extra_tags='error')
            return HttpResponseRedirect(reverse('home'))

        logger.info(
            f"Request for URL: {request.path}. Method: {request.method}. User: {request.user}. "
            f"Status Code {response.status_code}")

        return response
