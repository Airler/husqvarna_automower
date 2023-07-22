"""Platform for Husqvarna Automower basic entity."""

import logging
from datetime import datetime

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from . import AutomowerDataUpdateCoordinator
from .const import DOMAIN, HUSQVARNA_URL

_LOGGER = logging.getLogger(__name__)


class AutomowerEntity(CoordinatorEntity[AutomowerDataUpdateCoordinator]):
    """Defining the Automower Basic Entity."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, idx) -> None:
        """Initialize AutomowerEntity."""
        super().__init__(coordinator, context=idx)
        self.idx = idx
        self.mower = coordinator.data["data"][self.idx]
        mower_attributes = self.get_mower_attributes()
        self.mower_id = self.mower["id"]
        self.mower_name = mower_attributes["system"]["name"]
        self.model_name = mower_attributes["system"]["model"]

        self._available = self.get_mower_attributes()["metadata"]["connected"]

    def get_mower_attributes(self) -> dict:
        """Get the mower attributes of the current mower."""
        return self.coordinator.data["data"][self.idx]["attributes"]

    def datetime_object(self, timestamp) -> datetime:
        """Convert the mower local timestamp to a UTC datetime object."""
        if timestamp != 0:
            naive = datetime.utcfromtimestamp(timestamp / 1000)
            local = dt_util.as_local(naive)
        if timestamp == 0:
            local = None
        return local

    @property
    def device_info(self) -> DeviceInfo:
        """Define the DeviceInfo for the mower."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.mower_id)},
            name=self.mower_name,
            manufacturer="Husqvarna",
            model=self.model_name,
            configuration_url=HUSQVARNA_URL,
            suggested_area="Garden",
        )

    @property
    def is_home(self):
        """Return True if the mower is located at the charging station."""
        if self.get_mower_attributes()["mower"]["activity"] in [
            "PARKED_IN_CS",
            "CHARGING",
        ]:
            return True
        return False

    @property
    def should_poll(self) -> bool:
        """Return True if the device is available."""
        return False
