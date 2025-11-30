"""Token storage for persistent access token management."""

from datetime import datetime
from pathlib import Path
from typing import NamedTuple


class TokenData(NamedTuple):
    """Token data structure."""

    access_token: str
    expired_at: datetime


class TokenStorage:
    """Manage access token persistence in .env file."""

    TOKEN_KEY = "AIO123PAN_CACHED_ACCESS_TOKEN"
    EXPIRY_KEY = "AIO123PAN_CACHED_TOKEN_EXPIRY"

    def __init__(self, env_file: str | Path | None = None) -> None:
        if env_file is None:
            env_file = Path.cwd() / ".env"
        self.env_file = Path(env_file)

    def save(self, access_token: str, expired_at: datetime) -> None:
        """Save token to .env file.

        Args:
            access_token: Access token string
            expired_at: Token expiration datetime
        """
        lines = []
        token_written = False
        expiry_written = False

        if self.env_file.exists():
            with open(self.env_file, encoding="utf-8") as f:
                for line in f:
                    stripped = line.strip()
                    if stripped.startswith(f"{self.TOKEN_KEY}="):
                        lines.append(f"{self.TOKEN_KEY}={access_token}\n")
                        token_written = True
                    elif stripped.startswith(f"{self.EXPIRY_KEY}="):
                        lines.append(f"{self.EXPIRY_KEY}={expired_at.isoformat()}\n")
                        expiry_written = True
                    else:
                        lines.append(line)

        if not token_written:
            lines.append(f"{self.TOKEN_KEY}={access_token}\n")
        if not expiry_written:
            lines.append(f"{self.EXPIRY_KEY}={expired_at.isoformat()}\n")

        self.env_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.env_file, "w", encoding="utf-8") as f:
            f.writelines(lines)

    def load(self) -> TokenData | None:
        """Load token from .env file.

        Returns:
            TokenData if valid token exists, None otherwise
        """
        if not self.env_file.exists():
            return None

        access_token = None
        expired_at_str = None

        with open(self.env_file, encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if stripped.startswith(f"{self.TOKEN_KEY}="):
                    access_token = stripped.split("=", 1)[1]
                elif stripped.startswith(f"{self.EXPIRY_KEY}="):
                    expired_at_str = stripped.split("=", 1)[1]

        if not access_token or not expired_at_str:
            return None

        try:
            expired_at = datetime.fromisoformat(expired_at_str)

            if datetime.now(expired_at.tzinfo) >= expired_at:
                return None

            return TokenData(access_token=access_token, expired_at=expired_at)
        except (ValueError, AttributeError):
            return None

    def clear(self) -> None:
        """Clear stored token from .env file."""
        if not self.env_file.exists():
            return

        lines = []
        with open(self.env_file, encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if not stripped.startswith(f"{self.TOKEN_KEY}=") and not stripped.startswith(f"{self.EXPIRY_KEY}="):
                    lines.append(line)

        with open(self.env_file, "w", encoding="utf-8") as f:
            f.writelines(lines)
