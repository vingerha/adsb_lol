"""ConfigFlow for GTFS integration."""
from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import selector

from .const import (
    DOMAIN, 
    CONF_NAME,
    CONF_REFRESH_INTERVAL,
    ATTR_DEFAULT_REFRESH_INTERVAL, 
    CONF_URL,
    CONF_EXTRACT_TYPE,
    CONF_EXTRACT_PARAM,
    CONF_EXTRACT_PARAM_INPUT,
    ATTR_DEFAULT_URL,
    CONF_EXTRACT_TYPE,
    CONF_RADIUS,
    ATTR_DEFAULT_RADIUS,
    CONF_DEVICE_TRACKER_ID,
    CONF_ALTITUDE_LIMIT,
    ATTR_DEFAULT_ALTITUDE_LIMIT
)    

from .adsb_helper import (
    get_flight,
)

_LOGGER = logging.getLogger(__name__)

@config_entries.HANDLERS.register(DOMAIN)
class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for GTFS."""

    VERSION = 1

    def __init__(self) -> None:
        """Init ConfigFlow."""
        self._pygtfs = ""
        self._data: dict[str, str] = {}
        self._user_inputs: dict = {}

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        """Handle the source."""
        errors: dict[str, str] = {}
        
        return self.async_show_menu(
            step_id="user",
            menu_options=["flight_details","flight_details_input","point_of_interest"],
            description_placeholders={
                "model": "Example model",
            }
        )
                   
    async def async_step_flight_details(self, user_input: dict | None = None) -> FlowResult:
        """Handle the source."""
        errors: dict[str, str] = {}      
        if user_input is None:
            return self.async_show_form(
                step_id="flight_details",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_EXTRACT_TYPE): selector.SelectSelector(selector.SelectSelectorConfig(options=["registration", "callsign", "icao"], translation_key="extract_type")),
                        vol.Required(CONF_EXTRACT_PARAM): str,
                        vol.Required(CONF_URL, default=ATTR_DEFAULT_URL): str,
                        vol.Required(CONF_NAME): str,
                    },
                ),
            )
        self._user_inputs.update(user_input)
        _LOGGER.debug(f"UserInputs Start End: {self._user_inputs}")
        return self.async_create_entry(
                title=user_input[CONF_NAME], data=self._user_inputs
            ) 

    async def async_step_flight_details_input(self, user_input: dict | None = None) -> FlowResult:
        """Handle the source."""
        errors: dict[str, str] = {}      
        if user_input is None:
            return self.async_show_form(
                step_id="flight_details_input",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_EXTRACT_TYPE): selector.SelectSelector(selector.SelectSelectorConfig(options=["registration", "callsign", "icao"], translation_key="extract_type")),
                        vol.Required(CONF_EXTRACT_PARAM_INPUT): selector.EntitySelector(
                                selector.EntitySelectorConfig(domain=["input_text","input_select"]),                          
                            ),
                        vol.Required(CONF_URL, default=ATTR_DEFAULT_URL): str,
                        vol.Required(CONF_NAME): str,
                    },
                ),
            )
        self._user_inputs.update(user_input)
        _LOGGER.debug(f"UserInputs Start End: {self._user_inputs}")
        return self.async_create_entry(
                title=user_input[CONF_NAME], data=self._user_inputs
            )             
            
    async def async_step_point_of_interest(self, user_input: dict | None = None) -> FlowResult:
        """Handle the source."""
        errors: dict[str, str] = {}      
        if user_input is None:
            return self.async_show_form(
                step_id="point_of_interest",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_DEVICE_TRACKER_ID): selector.EntitySelector(
                            selector.EntitySelectorConfig(domain=["person","zone"]),                          
                        ),
                        vol.Required(CONF_RADIUS, default=ATTR_DEFAULT_RADIUS): vol.All(vol.Coerce(int), vol.Range(min=0, max=440)),
                        vol.Required(CONF_ALTITUDE_LIMIT, default=ATTR_DEFAULT_ALTITUDE_LIMIT): vol.All(vol.Coerce(int), vol.Range(min=0, max=15)),
                        vol.Required(CONF_URL, default=ATTR_DEFAULT_URL): str,
                        vol.Required(CONF_NAME): str, 
                    },
                ),
            ) 
        user_input[CONF_EXTRACT_TYPE] = "point"            
        self._user_inputs.update(user_input)
        _LOGGER.debug(f"UserInputs Start End: {self._user_inputs}")
        
        return self.async_create_entry(
                title=user_input[CONF_NAME], data=self._user_inputs
            )            
                   
    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return ADSBOptionsFlowHandler(config_entry)


class ADSBOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry
        self._data: dict[str, str] = {}
        self._user_inputs: dict = {}

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is None:
            return self.async_show_form(
                step_id="init",
                data_schema=vol.Schema(
                    {
                        vol.Optional(CONF_REFRESH_INTERVAL, default=self.config_entry.options.get(CONF_REFRESH_INTERVAL, ATTR_DEFAULT_REFRESH_INTERVAL)): vol.All(vol.Coerce(int), vol.Range(min=1)),
                    },
                ),
            ) 
        self._user_inputs.update(user_input)
        _LOGGER.debug(f"UserInputs Options Init: {self._user_inputs}")
        return self.async_create_entry(title="", data=self._user_inputs)            