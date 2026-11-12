"""Config flow for Viomi V8 Vacuum."""
from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_TOKEN
from homeassistant.helpers import config_validation as cv

from .client import ViomiV8Client
from .const import CONF_FIRMWARE, CONF_MAC, CONF_MODEL, DOMAIN, SUPPORTED_MODELS

_LOGGER = logging.getLogger(__name__)

SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_TOKEN): vol.All(cv.string, vol.Length(min=32, max=32)),
    }
)


def _probe(host: str, token: str) -> dict[str, str]:
    """Talk to the device once and return its identity (blocking)."""
    info = ViomiV8Client(host, token).info()
    return {
        CONF_MODEL: info.model or "",
        CONF_MAC: info.mac_address or "",
        CONF_FIRMWARE: info.firmware_version or "",
    }


class ViomiV8ConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def _async_validate(
        self, user_input: Mapping[str, Any]
    ) -> tuple[dict[str, str] | None, str | None]:
        """Return (identity, error_key)."""
        try:
            ident = await self.hass.async_add_executor_job(
                _probe, user_input[CONF_HOST], user_input[CONF_TOKEN]
            )
        except Exception:  # noqa: BLE001 - miio raises many types
            _LOGGER.debug("Probe failed", exc_info=True)
            return None, "cannot_connect"
        if ident[CONF_MODEL] not in SUPPORTED_MODELS:
            _LOGGER.warning("Unsupported model reported: %s", ident[CONF_MODEL])
            return None, "wrong_model"
        return ident, None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            ident, error = await self._async_validate(user_input)
            if error is None and ident is not None:
                unique = ident[CONF_MAC] or f"{ident[CONF_MODEL]}-{user_input[CONF_HOST]}"
                await self.async_set_unique_id(unique)
                self._abort_if_unique_id_configured(
                    updates={
                        CONF_HOST: user_input[CONF_HOST],
                        CONF_TOKEN: user_input[CONF_TOKEN],
                    }
                )
                return self.async_create_entry(
                    title="Viomi V8",
                    data={**user_input, **ident},
                )
            errors["base"] = error or "cannot_connect"
        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(SCHEMA, user_input),
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Change host/token (for example after the router hands out a new IP)."""
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}
        if user_input is not None:
            ident, error = await self._async_validate(user_input)
            if error is None and ident is not None:
                await self.async_set_unique_id(
                    ident[CONF_MAC] or f"{ident[CONF_MODEL]}-{user_input[CONF_HOST]}"
                )
                self._abort_if_unique_id_mismatch(reason="wrong_device")
                return self.async_update_reload_and_abort(
                    entry, data_updates={**user_input, **ident}
                )
            errors["base"] = error or "cannot_connect"
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self.add_suggested_values_to_schema(
                SCHEMA, user_input or dict(entry.data)
            ),
            errors=errors,
        )
