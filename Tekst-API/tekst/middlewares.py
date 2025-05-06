import re

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class CookieTypeChoiceMiddleware(BaseHTTPMiddleware):
    _TRUTHY_VALS = ("true", "on", "1", "yes")

    def __init__(
        self,
        app,
        *,
        login_path_suffix="/auth/cookie/login",
        form_field_name="persistent",
    ):
        super().__init__(app)
        self.login_path_suffix = login_path_suffix
        self.form_field_name = form_field_name

    async def dispatch(self, request: Request, call_next):
        await request.body()  # make starlette cache the request body
        response = await call_next(request)  # pass on the request

        if request.url.path.endswith(self.login_path_suffix):
            # request was to ...<login_path_suffix>
            form_data = await request.form()
            if form_data.get(self.form_field_name, "").lower() not in self._TRUTHY_VALS:
                # the request is missing `form_field_name` or the value is falsy,
                # so we have to force any "set-cookie" headers of the response to
                # trigger the creation of session cookies instead of persistent cookies
                for k, v in response.headers.items():
                    if k.lower() == "set-cookie":
                        response.headers[k] = re.sub(
                            r"Max-Age=\d+ *;* *",
                            "",
                            response.headers[k],
                            flags=re.IGNORECASE,
                        )

        return response
