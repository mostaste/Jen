########################################################################
########################        Libraries       ########################

"""
Tiny helper for Shelly Plus 2PM.

This is intentionally minimal:
- Uses the Gen2 HTTP RPC endpoints (/rpc/...)
- Focuses on Switch + basic Cover (roller shutter) control.
- Returns raw dicts/strings; Fay will do the pretty talking.

You can expand this later (inputs, WiFi status, etc.)
Also IR Controller to tap into Infared Waves ( TV, Air-Con, etc.)
"""

from __future__ import annotations
from typing import Any, Dict, Optional

import time
import requests

########################################################################
#######################          Shelly          #######################

class ShellyError(Exception):
    """Generic error for Shelly operations."""

class ShellyManager:
    """
    Registry of Shelly Plus 2PM devices.

    device_map: { logical_name -> host_ip }
    Example: { "bedroom_lights": "192.168.1.50" }
    """

    def __init__(self, device_map: Optional[Dict[str, str]] = None) -> None:
        self.device_map = device_map or {}
        self._instances: Dict[str, ShellyPlus2PM] = {}

    def get_device(self, name_or_ip: str) -> ShellyPlus2PM:
        """
        Accept either:
        - a logical name in device_map ("bedroom_lights")
        - a raw IP/host ("192.168.1.50")
        """
        host = self.device_map.get(name_or_ip, name_or_ip)
        if host not in self._instances: self._instances[host] = ShellyPlus2PM(host)
        return self._instances[host]

class ShellyPlus2PM:
    """
    Wraps a single Shelly Plus 2PM device.

    host: IP or hostname, e.g. "192.168.1.123"
    """

    # ---------- Init ----------

    def __init__(self, host: str, *, username: Optional[str] = None, password: Optional[str] = None, timeout: float = 1.5, retries: int = 10, retry_delay: float = 0.25, retry_backoff: float = 1.2, retry_forever: bool = False) -> None:
        self.host = host.strip().rstrip("/")
        self.auth = (username, password) if username and password else None
        self.timeout = timeout

        self.retries = retries
        self.retry_delay = retry_delay
        self.retry_backoff = retry_backoff
        self.retry_forever = retry_forever

    # ---------- Low-Level Helpers ----------

    def _url(self, path: str) -> str:
        path = path.lstrip("/")
        return f"http://{self.host}/{path}"

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        attempt = 0
        delay = self.retry_delay
        last_err = None

        while True:
            attempt += 1
            try:
                resp = requests.get(
                    self._url(path),
                    params=params or {},
                    auth=self.auth,
                    timeout=self.timeout,
                )
                resp.raise_for_status()

                try:
                    return resp.json()
                except ValueError:
                    return {"raw": resp.text}

            except requests.HTTPError as e:
                last_err = e
                status = getattr(e.response, "status_code", None)

                # Bad request / auth / missing endpoint usually won't be fixed by retrying
                if status and 400 <= status < 500 and status not in (408, 429):
                    raise ShellyError(f"HTTP {status}: {e}") from e

            except Exception as e:
                last_err = e

            if not self.retry_forever and attempt >= self.retries:
                raise ShellyError(f"after {attempt} attempts: {last_err}") from last_err

            time.sleep(delay)
            delay = min(delay * self.retry_backoff, 2.0)

    '''
    def __init__(self, host: str, *, username: Optional[str] = None, password: Optional[str] = None, timeout: float = 3.0) -> None:
        self.host = host.strip().rstrip("/")
        self.auth = (username, password) if username and password else None
        self.timeout = timeout

    # ---------- Low-Level Helpers ----------

    def _url(self, path: str) -> str:
        path = path.lstrip("/")
        return f"http://{self.host}/{path}"

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        try:
            resp = requests.get(
                self._url(path),
                params=params or {},
                auth=self.auth,
                timeout=self.timeout,
            )
            resp.raise_for_status()
            try:                    return resp.json()
            except ValueError:      return {"raw": resp.text}               # some endpoints just reply with plain text
        except Exception as e:      raise ShellyError(str(e)) from e        # noqa: BLE001
    '''

    # ---------- Switch / Relay (2x10A) ----------

    def switch_get_status(self, channel: int = 0) -> Dict[str, Any]:
        """
        Get full status for a relay channel (0 = first, 1 = second).

        Uses /rpc/Switch.GetStatus?id=<channel>
        """
        return self._get("rpc/Switch.GetStatus", {"id": channel})

    def switch_set(self, channel: int = 0, on: bool = True) -> Dict[str, Any]:
        """
        Turn a relay ON or OFF.

        Uses /rpc/Switch.Set?id=<channel>&on=true/false
        """
        return self._get("rpc/Switch.Set", {"id": channel, "on": "true" if on else "false"})

    def switch_toggle(self, channel: int = 0) -> Dict[str, Any]:
        """
        Toggle a relay.

        Uses /rpc/Switch.toggle?id=<channel>
        """
        return self._get("rpc/Switch.toggle", {"id": channel})

    # ---------- Roller Shutter / Cover Mode (optional) ----------

    def cover_get_status(self, cover_id: int = 0) -> Dict[str, Any]:
        return self._get("rpc/Cover.GetStatus", {"id": cover_id})

    def cover_open(self, cover_id: int = 0, duration: Optional[int] = None) -> Dict[str, Any]:
        params: Dict[str, Any] = {"id": cover_id}
        if duration is not None:    params["duration"] = duration
        return self._get("rpc/Cover.Open", params)

    def cover_close(self, cover_id: int = 0, duration: Optional[int] = None) -> Dict[str, Any]:
        params: Dict[str, Any] = {"id": cover_id}
        if duration is not None:
            params["duration"] = duration
        return self._get("rpc/Cover.Close", params)

    def cover_stop(self, cover_id: int = 0) -> Dict[str, Any]:
        return self._get("rpc/Cover.Stop", {"id": cover_id})

    # ---------- Door Lock (2x20A) ----------

########################################################################