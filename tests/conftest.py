"""Shared pytest fixtures for VARTA Modbus tests."""

import pytest


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations for Home Assistant config-flow tests."""
    yield
