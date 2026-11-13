"""Two-Node Lumped Parameter Battery Thermal Observer.

Responsibility:
    Estimate battery core temperature and surface temperature dynamics from current
    and measured ambient/surface boundary conditions using a calibrated 2-node thermal model.

Vocabulary Constraints (Mandatory):
    - ALWAYS write: "estimated core temperature".
    - NEVER write: "measured core temperature" or "thermal runaway prediction".

Current Sign Convention:
    Current I > 0 denotes DISCHARGE. Documented in all estimators.

MAY import:
    stdlib, numpy, heatsense.domain.value_objects, heatsense.domain.entities, heatsense.domain.errors.

MUST NOT import:
    application, infrastructure, interfaces, simulation, pydantic, fastapi, serial, sqlite3, firmware.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ThermalParameters:
    """Calibrated thermal parameters for 18650 cylindrical cell."""

    c_core: float = 62.6  # Core heat capacity (J/K)
    c_surf: float = 25.0  # Surface heat capacity (J/K)
    r_cond: float = 0.59  # Conduction resistance core -> surface (K/W)
    r_conv: float = 23.50  # Convection resistance surface -> ambient (K/W)
    total_resistance_ohm: float = 0.0642 + 0.0746 + 0.0314  # Rs + R1 + R2


@dataclass(frozen=True, slots=True)
class ThermalStepResult:
    """State snapshot from one thermal observer integration step."""

    t_core_estimated_c: float
    t_surface_estimated_c: float
    thermal_gradient_c: float
    heat_generated_w: float
    surface_residual_c: float


class TwoNodeThermalObserver:
    """Dynamic Two-Node (Core-Surface) Thermal Observer.
    
    Equations:
        C_core * d(T_core)/dt = Q_gen - (T_core - T_surf) / R_cond
        C_surf * d(T_surf)/dt = (T_core - T_surf) / R_cond - (T_surf - T_amb) / R_conv
    """

    def __init__(self, params: ThermalParameters | None = None, initial_temp_c: float = 24.0) -> None:
        self._p = params or ThermalParameters()
        self._t_amb = float(initial_temp_c)
        self._t_core = float(initial_temp_c)
        self._t_surf = float(initial_temp_c)

    @property
    def t_core_estimated_c(self) -> float:
        """Current estimated core temperature in Celsius."""
        return self._t_core

    @property
    def t_surface_estimated_c(self) -> float:
        """Current estimated surface temperature in Celsius."""
        return self._t_surf

    @property
    def thermal_gradient_c(self) -> float:
        """Internal thermal gradient: T_core - T_surface in Celsius."""
        return self._t_core - self._t_surf

    def step(self, dt_s: float, i_load_a: float, t_surface_measured_c: float) -> ThermalStepResult:
        """Integrate thermal equations forward by dt_s seconds.
        
        Sub-stepping is used to maintain Euler integration stability.
        """
        dt = max(dt_s, 0.001)

        # Internal Joule heating: Q_gen = I^2 * R_total
        q_gen = (i_load_a**2) * self._p.total_resistance_ohm

        n_sub = max(1, int(math.ceil(dt / 1.0)))
        sub_dt = dt / n_sub

        for _ in range(n_sub):
            dt_core = (q_gen - (self._t_core - self._t_surf) / self._p.r_cond) / self._p.c_core
            dt_surf = (
                (self._t_core - self._t_surf) / self._p.r_cond - (self._t_surf - self._t_amb) / self._p.r_conv
            ) / self._p.c_surf

            self._t_core += dt_core * sub_dt
            self._t_surf += dt_surf * sub_dt

        residual_c = t_surface_measured_c - self._t_surf

        return ThermalStepResult(
            t_core_estimated_c=self._t_core,
            t_surface_estimated_c=self._t_surf,
            thermal_gradient_c=self._t_core - self._t_surf,
            heat_generated_w=q_gen,
            surface_residual_c=residual_c,
        )

