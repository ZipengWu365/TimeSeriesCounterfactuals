"""Optional integrations and adapter metadata for external causal / forecasting packages."""

from .adapters import (
    CImpactAdapter,
    CImpactAdapter,
    CausalPyAdapter,
    DartsForecastAdapter,
    GenericForecastCounterfactualAdapter,
    MetadataOnlyAdapter,
    OptionalDependencyError,
    PysynconPanelAdapter,
    SCPIAdapter,
    StatsForecastCounterfactualAdapter,
    SyntheticControlMethodsAdapter,
)
from .cards import (
    AdapterCard,
    adapter_catalog,
    get_adapter_card,
    group_install_profiles,
    list_adapter_cards,
    recommend_adapter_stack,
)
from .causalimpact import TFPCausalImpactAdapter

__all__ = [
    "AdapterCard",
    "adapter_catalog",
    "get_adapter_card",
    "group_install_profiles",
    "list_adapter_cards",
    "recommend_adapter_stack",
    "OptionalDependencyError",
    "MetadataOnlyAdapter",
    "GenericForecastCounterfactualAdapter",
    "PysynconPanelAdapter",
    "SCPIAdapter",
    "SyntheticControlMethodsAdapter",
    "CausalPyAdapter",
    "CImpactAdapter",
    "DartsForecastAdapter",
    "StatsForecastCounterfactualAdapter",
    "TFPCausalImpactAdapter",
]
