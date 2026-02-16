#!/usr/bin/env python3
"""Simple Island Demo - Pygame visualization of PyPSI agent."""

from __future__ import annotations

import sys
from dataclasses import dataclass

import pygame

sys.path.insert(0, "src")

from pypsi.action import create_default_action_library
from pypsi.environment import (
    Direction,
    GridPos,
    ResourceType,
    TerrainType,
    create_simple_island,
)
from pypsi.needs import Motivator, Motivselektor, Motive, NeedTankSystem, NeedType
from pypsi.perception import create_default_perception_system


COLORS = {
    "water": (20, 60, 120),
    "shallow": (60, 120, 180),
    "sand": (240, 220, 160),
    "grass": (80, 160, 80),
    "forest": (40, 100, 40),
    "mountain": (120, 120, 120),
    "food": (255, 100, 100),
    "water_resource": (100, 150, 255),
    "shelter": (180, 140, 100),
    "agent": (255, 255, 0),
    "agent_outline": (200, 200, 0),
    "text": (255, 255, 255),
    "panel_bg": (40, 40, 50),
    "bar_bg": (60, 60, 70),
    "hunger_bar": (255, 150, 50),
    "thirst_bar": (50, 150, 255),
    "energy_bar": (150, 255, 50),
    "certainty_bar": (200, 200, 200),
    "competence_bar": (255, 200, 50),
    "affiliation_bar": (255, 100, 200),
}


@dataclass
class SimulationConfig:
    grid_size: int = 20
    fps: int = 30
    sim_speed: float = 1.0
    island_width: int = 40
    island_height: int = 30
    panel_width: int = 300


class PSIBot:
    def __init__(self, start_pos: GridPos) -> None:
        self.position = start_pos
        self.need_system = NeedTankSystem()
        self.perception = create_default_perception_system()
        self.action_library = create_default_action_library()
        
        self.motivators = {
            need_type: Motivator(need_type=need_type)
            for need_type in NeedType
        }
        self.motive_selector = Motivselektor(min_strength_threshold=0.01)
        
        self.current_motive: Motive | None = None
        self.action_cooldown: float = 0.0
        self.last_action_result: str = ""
        
    def update(self, island, dt: float, elapsed: float) -> None:
        self.need_system.update_all(dt)
        
        bedarfe = self.need_system.get_all_bedarfe()
        for need_type, motivator in self.motivators.items():
            motivator.accumulate(bedarfe[need_type])
            motivator.decay(dt)
        
        if self.action_cooldown > 0:
            self.action_cooldown -= dt
            return
        
        from pypsi.action import Action
        from pypsi.environment import Percept
        
        percept = self.perception.perceive(island, self.position)
        executable_actions = self.action_library.get_executable_actions(
            island, self.position, percept, self.need_system
        )
        
        if not executable_actions:
            self.last_action_result = "No executable actions"
            self.action_cooldown = 0.5
            return
        
        motives = []
        for action in executable_actions:
            for need_type in NeedType:
                value = action.get_value_for_need(need_type)
                if value > 0:
                    motive = Motive(
                        motivator=self.motivators[need_type],
                        goal=action
                    )
                    motives.append(motive)
        
        selected = self.motive_selector.select_motive(motives)
        self.current_motive = selected
        
        if selected is None:
            self.last_action_result = "No motive selected"
            self.action_cooldown = 0.5
            return
        
        action = selected.goal
        if isinstance(action, Action):
            outcome = action.execute(island, self.position, self.need_system)
            self.last_action_result = outcome.message
            
            if outcome.new_position is not None:
                island.vacate_tile(self.position)
                self.position = outcome.new_position
            
            self.action_cooldown = 0.3


class SimpleIslandDemo:
    def __init__(self, config: SimulationConfig | None = None) -> None:
        self.config = config or SimulationConfig()
        
        self.island = create_simple_island(
            self.config.island_width,
            self.config.island_height
        )
        
        start_pos = self._find_start_position()
        self.agent = PSIBot(start_pos)
        self.island.occupy_tile(start_pos, "agent")
        
        pygame.init()
        
        grid_width = self.config.island_width * self.config.grid_size
        grid_height = self.config.island_height * self.config.grid_size
        self.window_width = grid_width + self.config.panel_width
        self.window_height = max(grid_height, 600)
        
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("PyPSI - Simple Island Demo")
        
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 20)
        
        self.running = True
        self.paused = False
        self.elapsed = 0.0
        
    def _find_start_position(self) -> GridPos:
        center_x = self.config.island_width // 2
        center_y = self.config.island_height // 2
        
        for radius in range(min(center_x, center_y)):
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    if abs(dx) != radius and abs(dy) != radius:
                        continue
                    pos = GridPos(center_x + dx, center_y + dy)
                    tile = self.island.get_tile(pos)
                    if tile and tile.is_passable():
                        return pos
        
        return GridPos(center_x, center_y)
    
    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(self.config.fps) / 1000.0
            dt *= self.config.sim_speed
            
            self._handle_events()
            
            if not self.paused:
                self.elapsed += dt
                self.agent.update(self.island, dt, self.elapsed)
            
            self._render()
        
        pygame.quit()
    
    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_r:
                    self._reset_simulation()
                elif event.key in (pygame.K_PLUS, pygame.K_EQUALS):
                    self.config.sim_speed = min(5.0, self.config.sim_speed + 0.5)
                elif event.key == pygame.K_MINUS:
                    self.config.sim_speed = max(0.1, self.config.sim_speed - 0.5)
    
    def _reset_simulation(self) -> None:
        self.island.vacate_tile(self.agent.position)
        self.island = create_simple_island(
            self.config.island_width,
            self.config.island_height
        )
        start_pos = self._find_start_position()
        self.agent = PSIBot(start_pos)
        self.island.occupy_tile(start_pos, "agent")
        self.elapsed = 0.0
    
    def _render(self) -> None:
        self.screen.fill((20, 20, 30))
        self._render_island()
        self._render_agent()
        self._render_panel()
        pygame.display.flip()
    
    def _render_island(self) -> None:
        gs = self.config.grid_size
        
        for y, row in enumerate(self.island.tiles):
            for x, tile in enumerate(row):
                rect = pygame.Rect(x * gs, y * gs, gs, gs)
                color = self._get_terrain_color(tile.terrain)
                pygame.draw.rect(self.screen, color, rect)
                
                if tile.has_resource():
                    resource_color = self._get_resource_color(tile.resource)
                    center = (x * gs + gs // 2, y * gs + gs // 2)
                    pygame.draw.circle(self.screen, resource_color, center, gs // 4)
                
                pygame.draw.rect(self.screen, (30, 30, 40), rect, 1)
    
    def _get_terrain_color(self, terrain: TerrainType) -> tuple[int, int, int]:
        return {
            TerrainType.WATER: COLORS["water"],
            TerrainType.SHALLOW: COLORS["shallow"],
            TerrainType.SAND: COLORS["sand"],
            TerrainType.GRASS: COLORS["grass"],
            TerrainType.FOREST: COLORS["forest"],
            TerrainType.MOUNTAIN: COLORS["mountain"],
        }.get(terrain, (100, 100, 100))
    
    def _get_resource_color(self, resource: ResourceType) -> tuple[int, int, int]:
        return {
            ResourceType.FOOD: COLORS["food"],
            ResourceType.WATER: COLORS["water_resource"],
            ResourceType.SHELTER: COLORS["shelter"],
            ResourceType.NONE: (0, 0, 0),
        }.get(resource, (200, 200, 200))
    
    def _render_agent(self) -> None:
        gs = self.config.grid_size
        x = self.agent.position.x * gs
        y = self.agent.position.y * gs
        center = (x + gs // 2, y + gs // 2)
        radius = gs // 2 - 2
        
        pygame.draw.circle(self.screen, COLORS["agent_outline"], center, radius)
        pygame.draw.circle(self.screen, COLORS["agent"], center, radius - 2)
        pygame.draw.circle(self.screen, (0, 0, 0), center, 3)
    
    def _render_panel(self) -> None:
        gs = self.config.grid_size
        grid_width = self.config.island_width * gs
        panel_x = grid_width + 10
        
        panel_rect = pygame.Rect(grid_width, 0, self.config.panel_width, self.window_height)
        pygame.draw.rect(self.screen, COLORS["panel_bg"], panel_rect)
        
        y_offset = 20
        
        title = self.font.render("PyPSI Agent Status", True, COLORS["text"])
        self.screen.blit(title, (panel_x, y_offset))
        y_offset += 40
        
        sim_info = [
            f"Time: {self.elapsed:.1f}s",
            f"Speed: {self.config.sim_speed:.1f}x",
            f"Status: {'PAUSED' if self.paused else 'Running'}",
        ]
        for info in sim_info:
            text = self.font_small.render(info, True, COLORS["text"])
            self.screen.blit(text, (panel_x, y_offset))
            y_offset += 25
        
        y_offset += 20
        
        needs = [
            ("Hunger", NeedType.HUNGER, COLORS["hunger_bar"]),
            ("Thirst", NeedType.THIRST, COLORS["thirst_bar"]),
            ("Energy", NeedType.ENERGY, COLORS["energy_bar"]),
            ("Certainty", NeedType.CERTAINTY, COLORS["certainty_bar"]),
            ("Competence", NeedType.COMPETENCE, COLORS["competence_bar"]),
            ("Affiliation", NeedType.AFFILIATION, COLORS["affiliation_bar"]),
        ]
        
        for name, need_type, color in needs:
            tank = self.agent.need_system.get_tank(need_type)
            level = tank.current_level
            
            label = self.font_small.render(f"{name}:", True, COLORS["text"])
            self.screen.blit(label, (panel_x, y_offset))
            
            bar_rect = pygame.Rect(panel_x + 80, y_offset + 2, 150, 16)
            pygame.draw.rect(self.screen, COLORS["bar_bg"], bar_rect)
            
            fill_width = int(150 * level)
            fill_rect = pygame.Rect(panel_x + 80, y_offset + 2, fill_width, 16)
            pygame.draw.rect(self.screen, color, fill_rect)
            
            if tank.is_critical():
                pygame.draw.rect(self.screen, COLORS["food"], bar_rect, 2)
            
            value_text = self.font_small.render(f"{level:.0%}", True, COLORS["text"])
            self.screen.blit(value_text, (panel_x + 235, y_offset + 1))
            
            y_offset += 28
        
        y_offset += 20
        
        # Most urgent need
        urgent_need, bedarf = self.agent.get_most_urgent_need()
        urgent_text = self.font_small.render(
            f"Most Urgent: {urgent_need.name} ({bedarf:.2f})", 
            True, COLORS["food"] if bedarf > 0.5 else COLORS["text"]
        )
        self.screen.blit(urgent_text, (panel_x, y_offset))
        y_offset += 30
        
        # Current motive
        if self.agent.current_motive:
            motive_text = self.font_small.render(
                f"Motive: {self.agent.current_motive.get_need_type().name}",
                True, COLORS["text"]
            )
            self.screen.blit(motive_text, (panel_x, y_offset))
            y_offset += 25
        
        # Last action result
        y_offset += 10
        result_text = self.font_small.render(
            f"Last: {self.agent.last_action_result[:40]}",
            True, COLORS["text"]
        )
        self.screen.blit(result_text, (panel_x, y_offset))
        y_offset += 40
        
        # Controls
        controls = [
            "Controls:",
            "SPACE - Pause/Resume",
            "R - Reset simulation",
            "+/- - Adjust speed",
            "ESC/Q - Quit",
        ]
        for control in controls:
            text = self.font_small.render(control, True, (150, 150, 150))
            self.screen.blit(text, (panel_x, y_offset))
            y_offset += 22


def main():
    print("Starting PyPSI Simple Island Demo...")
    print("Controls:")
    print("  SPACE - Pause/Resume")
    print("  R - Reset simulation")
    print("  +/- - Adjust simulation speed")
    print("  ESC or Q - Quit")
    print()
    
    demo = SimpleIslandDemo()
    demo.run()
    print("Demo ended.")


if __name__ == "__main__":
    main()
