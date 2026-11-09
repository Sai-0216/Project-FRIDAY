import json
import urllib.error
import urllib.request
from urllib.parse import urlsplit

from . import config


class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _open_request(request, timeout):
    opener = urllib.request.build_opener(_NoRedirectHandler)
    return opener.open(request, timeout=timeout)


class OpenJarvisClient:

    def __init__(self):
        self.base_url = config.BASE_URL.rstrip("/")
        self.model = config.MODEL
        self.timeout = config.REQUEST_TIMEOUT_SECONDS

        parsed = urlsplit(self.base_url)

        if (
            parsed.scheme != "http"
            or parsed.hostname != "127.0.0.1"
            or parsed.port != 8000
            or parsed.username is not None
            or parsed.password is not None
            or parsed.path not in ("", "/")
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError(
                "OpenJarvis must use http://127.0.0.1:8000."
            )

    def complete(self, prompt):
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("Prompt must be a non-empty string.")

        return self.complete_messages([
            {"role": "user", "content": prompt.strip()}
        ])

    def complete_messages(
        self,
        messages,
        max_tokens=None,
        temperature=None,
    ):
        if not isinstance(messages, list) or not messages:
            raise ValueError("Messages must be a non-empty list.")

        allowed_roles = {"system", "user", "assistant"}
        validated_messages = []
        total_chars = 0

        for message in messages:
            if not isinstance(message, dict):
                raise ValueError("Each message must be an object.")

            role = message.get("role")
            content = message.get("content")

            if role not in allowed_roles:
                raise ValueError("Message contains an unsupported role.")

            if not isinstance(content, str):
                raise ValueError("Message content must be a string.")

            total_chars += len(content)

            validated_messages.append({
                "role": role,
                "content": content,
            })

        if not validated_messages[-1]["content"].strip():
            raise ValueError("The final message must not be empty.")

        if total_chars > config.MAX_PROMPT_CHARS:
            raise ValueError("Messages exceed the configured size limit.")

        token_limit = (
            config.MAX_RESPONSE_TOKENS
            if max_tokens is None
            else max_tokens
        )

        temperature = (
            config.TEMPERATURE
            if temperature is None
            else temperature
        )

        if not isinstance(token_limit, int) or isinstance(token_limit, bool) or token_limit < 1:
            raise ValueError("max_tokens must be a positive integer.")

        if not isinstance(temperature, (int, float)) or isinstance(temperature, bool):
            raise ValueError("temperature must be numeric.")

        payload = {
            "model": self.model,
            "messages": validated_messages,
            "temperature": temperature,
            "max_tokens": token_limit,
        }

        request = urllib.request.Request(
            f"{self.base_url}/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with _open_request(request, timeout=self.timeout) as response:
                headers = getattr(response, "headers", {})
                content_length = headers.get("Content-Length")

                if content_length is not None:
                    try:
                        if int(content_length) > config.MAX_RESPONSE_BYTES:
                            raise RuntimeError(
                                "OpenJarvis response exceeds the size limit."
                            )
                    except ValueError:
                        raise RuntimeError(
                            "OpenJarvis returned an invalid content length."
                        )

                raw_data = response.read(config.MAX_RESPONSE_BYTES + 1)

                if len(raw_data) > config.MAX_RESPONSE_BYTES:
                    raise RuntimeError(
                        "OpenJarvis response exceeds the size limit."
                    )

                result = json.loads(raw_data.decode("utf-8"))

        except urllib.error.HTTPError as error:
            raise RuntimeError(
                f"OpenJarvis HTTP error: {error.code}"
            ) from error

        except (urllib.error.URLError, TimeoutError) as error:
            raise RuntimeError(
                f"OpenJarvis connection failed: {error}"
            ) from error

        if not isinstance(result, dict):
            raise RuntimeError(
                "OpenJarvis returned an invalid response structure."
            )

        choices = result.get("choices")

        if not isinstance(choices, list) or not choices:
            raise RuntimeError("OpenJarvis returned no completion.")

        first_choice = choices[0]

        if not isinstance(first_choice, dict):
            raise RuntimeError(
                "OpenJarvis returned an invalid completion structure."
            )

        message = first_choice.get("message")

        if not isinstance(message, dict):
            raise RuntimeError(
                "OpenJarvis returned an invalid message structure."
            )

        content = message.get("content")

        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("OpenJarvis returned an empty response.")

        return content.strip()
