"""
Module Interface Graphique - Interface Pygame pour le Morpion
Design moderne avec palette Orange / Blanc / Vert
"""

import pygame
import sys
import os
import math
from typing import Optional, Tuple, List
from enum import Enum

from environment import TicTacToeEnv
from agent import QLearningAgent, RandomAgent
from trainer import Trainer


class GameMode(Enum):
    """Modes de jeu disponibles."""
    MENU = 0
    HUMAN_VS_HUMAN = 1
    HUMAN_VS_AI = 2
    AI_VS_AI = 3
    TRAINING = 4
    EVALUATION = 5


class Colors:
    """Palette de couleurs moderne Orange/Blanc/Vert."""
    # Fond
    BACKGROUND = (255, 255, 255)
    BACKGROUND_SOFT = (250, 250, 250)

    # Orange (pour X et accents)
    ORANGE = (255, 140, 0)
    ORANGE_LIGHT = (255, 180, 80)
    ORANGE_DARK = (230, 120, 0)

    # Vert (pour O et succès)
    GREEN = (76, 175, 80)
    GREEN_LIGHT = (129, 199, 132)
    GREEN_DARK = (56, 142, 60)

    # Neutres
    GRAY_DARK = (66, 66, 66)
    GRAY_MEDIUM = (158, 158, 158)
    GRAY_LIGHT = (224, 224, 224)
    WHITE = (255, 255, 255)

    # Texte
    TEXT_PRIMARY = (33, 33, 33)
    TEXT_SECONDARY = (117, 117, 117)

    # Grille
    GRID = (200, 200, 200)

    # Boutons
    BUTTON_ORANGE = (255, 152, 0)
    BUTTON_ORANGE_HOVER = (255, 167, 38)
    BUTTON_GREEN = (76, 175, 80)
    BUTTON_GREEN_HOVER = (102, 187, 106)


class Button:
    """Bouton moderne avec effet de survol."""

    def __init__(self, x: int, y: int, width: int, height: int, text: str,
                 font: pygame.font.Font, color: Tuple, hover_color: Tuple):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.hovered = False
        self.shadow_offset = 4

    def draw(self, screen: pygame.Surface):
        """Dessine le bouton avec ombre et effet de survol."""
        # Ombre
        shadow_rect = self.rect.copy()
        shadow_rect.y += self.shadow_offset
        pygame.draw.rect(screen, Colors.GRAY_LIGHT, shadow_rect, border_radius=12)

        # Bouton principal
        color = self.hover_color if self.hovered else self.color
        draw_rect = self.rect.copy()
        if self.hovered:
            draw_rect.y -= 2
        pygame.draw.rect(screen, color, draw_rect, border_radius=12)

        # Texte
        text_surface = self.font.render(self.text, True, Colors.WHITE)
        text_rect = text_surface.get_rect(center=draw_rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, pos: Tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos)

    def update_hover(self, pos: Tuple[int, int]):
        self.hovered = self.rect.collidepoint(pos)


class PygameGUI:
    """Interface graphique moderne pour le Morpion."""

    DEFAULT_AGENT_PATH = "agent_trained.pkl"
    BACKGROUND_IMAGE_PATH = "images/bg_wds.jpg"

    def __init__(self, window_size: int = 480):
        pygame.init()
        pygame.display.set_caption("Morpion - Q-Learning")

        self.window_size = window_size
        self.window_height = window_size + 120
        self.cell_size = window_size // 3
        self.cell_padding = 28
        self.line_width = 6

        self.screen = pygame.display.set_mode((window_size, self.window_height))
        self.clock = pygame.time.Clock()

        # Charger l'image de fond
        self.background = self._load_background()

        # Polices système pour meilleure lisibilité (anti-aliasing)
        try:
            # Essayer d'utiliser des polices système de qualité
            self.font_title = pygame.font.SysFont('segoeui', 40, bold=True)
            self.font_subtitle = pygame.font.SysFont('segoeui', 18)
            self.font_large = pygame.font.SysFont('segoeui', 32, bold=True)
            self.font_medium = pygame.font.SysFont('segoeui', 22)
            self.font_small = pygame.font.SysFont('segoeui', 16)
        except:
            # Fallback sur Arial si Segoe UI non disponible
            self.font_title = pygame.font.SysFont('arial', 40, bold=True)
            self.font_subtitle = pygame.font.SysFont('arial', 18)
            self.font_large = pygame.font.SysFont('arial', 32, bold=True)
            self.font_medium = pygame.font.SysFont('arial', 22)
            self.font_small = pygame.font.SysFont('arial', 16)

        # État
        self.mode = GameMode.MENU
        self.env = TicTacToeEnv()
        self.agent: Optional[QLearningAgent] = None
        self.ai_delay = 500
        self.last_ai_move_time = 0
        self.game_message = ""
        self.highlighted_cell: Optional[int] = None

        # Animation
        self.animation_time = 0

        # Boutons
        self.menu_buttons: List[Button] = []
        self._create_menu_buttons()

        # Entraînement
        self.training_progress = ""
        self.is_processing = False

    def _load_background(self) -> Optional[pygame.Surface]:
        """Charge et prépare l'image de fond avec opacité."""
        try:
            bg = pygame.image.load(self.BACKGROUND_IMAGE_PATH)
            bg = pygame.transform.scale(bg, (self.window_size, self.window_height))

            # Appliquer une couche blanche semi-transparente pour réduire l'opacité
            overlay = pygame.Surface((self.window_size, self.window_height), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 180))  # Blanc avec 70% opacité
            bg.blit(overlay, (0, 0))

            return bg
        except Exception as e:
            print(f"Impossible de charger le fond: {e}")
            return None

    def _draw_background(self):
        """Dessine le fond (image ou couleur unie)."""
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(Colors.BACKGROUND)

    def _create_menu_buttons(self):
        """Crée les boutons du menu avec style moderne."""
        btn_width = 260
        btn_height = 45
        start_y = 160
        spacing = 58
        x = (self.window_size - btn_width) // 2

        buttons_config = [
            ("Humain vs Humain", GameMode.HUMAN_VS_HUMAN, Colors.BUTTON_ORANGE, Colors.BUTTON_ORANGE_HOVER),
            ("Humain vs IA", GameMode.HUMAN_VS_AI, Colors.BUTTON_GREEN, Colors.BUTTON_GREEN_HOVER),
            ("IA vs IA", GameMode.AI_VS_AI, Colors.BUTTON_ORANGE, Colors.BUTTON_ORANGE_HOVER),
            ("Entraîner l'agent", GameMode.TRAINING, Colors.BUTTON_GREEN, Colors.BUTTON_GREEN_HOVER),
            ("Évaluer l'agent", GameMode.EVALUATION, Colors.GRAY_MEDIUM, Colors.GRAY_DARK),
        ]

        self.menu_buttons = []
        for i, (text, mode, color, hover) in enumerate(buttons_config):
            btn = Button(x, start_y + i * spacing, btn_width, btn_height,
                        text, self.font_medium, color, hover)
            btn.mode = mode
            self.menu_buttons.append(btn)

    def load_agent(self) -> bool:
        if not os.path.exists(self.DEFAULT_AGENT_PATH):
            return False
        try:
            self.agent = QLearningAgent(player=1)
            self.agent.load(self.DEFAULT_AGENT_PATH)
            self.agent.epsilon = 0.0
            return True
        except Exception:
            self.agent = None
            return False

    def draw_menu(self):
        """Dessine le menu avec design moderne."""
        self._draw_background()

        # Décoration en haut (bande orange)
        pygame.draw.rect(self.screen, Colors.ORANGE, (0, 0, self.window_size, 8))

        # Titre avec X et O intégrés
        title_y = 55

        # Calculer la position pour centrer "X MORPION O"
        morpion_text = self.font_title.render("MORPION", True, Colors.ORANGE)
        morpion_width = morpion_text.get_width()
        total_width = morpion_width + 60  # espace pour X et O
        start_x = (self.window_size - total_width) // 2

        # Dessiner X à gauche
        x_pos = start_x + 12
        self._draw_styled_x(x_pos, title_y, 14)

        # Dessiner "MORPION"
        morpion_rect = morpion_text.get_rect(midleft=(start_x + 35, title_y))
        self.screen.blit(morpion_text, morpion_rect)

        # Dessiner O à droite
        o_pos = start_x + 35 + morpion_width + 15
        self._draw_styled_o(o_pos, title_y, 12)

        subtitle = self.font_subtitle.render("Q-Learning • Machine Learning", True, Colors.TEXT_SECONDARY)
        sub_rect = subtitle.get_rect(center=(self.window_size // 2, 95))
        self.screen.blit(subtitle, sub_rect)

        # Ligne décorative
        pygame.draw.line(self.screen, Colors.GRAY_LIGHT,
                        (60, 120), (self.window_size - 60, 120), 2)

        # Boutons
        for btn in self.menu_buttons:
            btn.draw(self.screen)

        # Statut de l'agent
        y_status = self.window_height - 55
        if os.path.exists(self.DEFAULT_AGENT_PATH):
            # Indicateur vert
            pygame.draw.circle(self.screen, Colors.GREEN, (self.window_size // 2 - 100, y_status), 8)
            status = "Agent entraîné prêt"
            color = Colors.GREEN_DARK
        else:
            # Indicateur orange
            pygame.draw.circle(self.screen, Colors.ORANGE, (self.window_size // 2 - 100, y_status), 8)
            status = "Aucun agent entraîné"
            color = Colors.ORANGE_DARK

        status_text = self.font_small.render(status, True, color)
        self.screen.blit(status_text, (self.window_size // 2 - 80, y_status - 8))

        # Instructions
        help_text = self.font_small.render("Appuyez sur ESC pour quitter", True, Colors.TEXT_SECONDARY)
        help_rect = help_text.get_rect(center=(self.window_size // 2, self.window_height - 25))
        self.screen.blit(help_text, help_rect)

        pygame.display.flip()

    def _draw_mini_x(self, x: int, y: int, size: int):
        """Dessine un petit X décoratif."""
        pygame.draw.line(self.screen, Colors.ORANGE, (x - size, y - size), (x + size, y + size), 3)
        pygame.draw.line(self.screen, Colors.ORANGE, (x + size, y - size), (x - size, y + size), 3)

    def _draw_mini_o(self, x: int, y: int, size: int):
        """Dessine un petit O décoratif."""
        pygame.draw.circle(self.screen, Colors.GREEN, (x, y), size, 3)

    def _draw_styled_x(self, x: int, y: int, size: int):
        """Dessine un X stylisé pour le titre."""
        # X avec effet d'épaisseur
        pygame.draw.line(self.screen, Colors.ORANGE_DARK, (x - size, y - size + 1), (x + size, y + size + 1), 5)
        pygame.draw.line(self.screen, Colors.ORANGE_DARK, (x + size, y - size + 1), (x - size, y + size + 1), 5)
        pygame.draw.line(self.screen, Colors.ORANGE, (x - size, y - size), (x + size, y + size), 4)
        pygame.draw.line(self.screen, Colors.ORANGE, (x + size, y - size), (x - size, y + size), 4)

    def _draw_styled_o(self, x: int, y: int, size: int):
        """Dessine un O stylisé pour le titre."""
        # O avec effet d'épaisseur
        pygame.draw.circle(self.screen, Colors.GREEN_DARK, (x + 1, y + 1), size, 4)
        pygame.draw.circle(self.screen, Colors.GREEN, (x, y), size, 3)

    def _draw_victory_x(self, x: int, y: int, size: int):
        """Dessine un grand X pour la victoire."""
        # X avec effet 3D
        # Ombre
        pygame.draw.line(self.screen, Colors.ORANGE_DARK,
                        (x - size + 2, y - size + 2), (x + size + 2, y + size + 2), 8)
        pygame.draw.line(self.screen, Colors.ORANGE_DARK,
                        (x + size + 2, y - size + 2), (x - size + 2, y + size + 2), 8)
        # Principal
        pygame.draw.line(self.screen, Colors.ORANGE,
                        (x - size, y - size), (x + size, y + size), 6)
        pygame.draw.line(self.screen, Colors.ORANGE,
                        (x + size, y - size), (x - size, y + size), 6)

    def _draw_victory_o(self, x: int, y: int, size: int):
        """Dessine un grand O pour la victoire."""
        # O avec effet 3D
        # Ombre
        pygame.draw.circle(self.screen, Colors.GREEN_DARK, (x + 2, y + 2), size, 8)
        # Principal
        pygame.draw.circle(self.screen, Colors.GREEN, (x, y), size, 6)

    def draw_grid(self):
        """Dessine la grille avec style moderne."""
        self._draw_background()

        # Bande décorative en haut
        pygame.draw.rect(self.screen, Colors.ORANGE, (0, 0, self.window_size, 6))

        # Grille avec coins arrondis (lignes épaisses)
        for i in range(1, 3):
            x = i * self.cell_size
            pygame.draw.line(self.screen, Colors.GRID, (x, 20), (x, self.window_size - 20), self.line_width)

        for i in range(1, 3):
            y = i * self.cell_size
            pygame.draw.line(self.screen, Colors.GRID, (20, y), (self.window_size - 20, y), self.line_width)

    def draw_x(self, cell: int, animated: bool = False):
        """Dessine un X orange stylisé."""
        row = cell // 3
        col = cell % 3
        center_x = col * self.cell_size + self.cell_size // 2
        center_y = row * self.cell_size + self.cell_size // 2
        size = self.cell_size // 2 - self.cell_padding

        # X avec dégradé effet
        for offset in range(3):
            alpha = 255 - offset * 40
            color = Colors.ORANGE if offset == 0 else Colors.ORANGE_LIGHT
            thickness = 12 - offset * 2

            pygame.draw.line(self.screen, color,
                           (center_x - size + offset, center_y - size + offset),
                           (center_x + size - offset, center_y + size - offset), thickness)
            pygame.draw.line(self.screen, color,
                           (center_x + size - offset, center_y - size + offset),
                           (center_x - size + offset, center_y + size - offset), thickness)

    def draw_o(self, cell: int, animated: bool = False):
        """Dessine un O vert stylisé."""
        row = cell // 3
        col = cell % 3
        center_x = col * self.cell_size + self.cell_size // 2
        center_y = row * self.cell_size + self.cell_size // 2
        radius = self.cell_size // 2 - self.cell_padding

        # O avec effet de profondeur
        pygame.draw.circle(self.screen, Colors.GREEN_LIGHT, (center_x + 2, center_y + 2), radius, 12)
        pygame.draw.circle(self.screen, Colors.GREEN, (center_x, center_y), radius, 10)

    def draw_symbol(self, cell: int, player: int):
        """Dessine le symbole approprié."""
        if player == 1:
            self.draw_x(cell)
        elif player == 2:
            self.draw_o(cell)

    def draw_highlight(self, cell: int):
        """Surligne une case avec effet subtil."""
        row = cell // 3
        col = cell % 3
        padding = 10
        rect = pygame.Rect(
            col * self.cell_size + padding,
            row * self.cell_size + padding,
            self.cell_size - 2 * padding,
            self.cell_size - 2 * padding
        )

        # Effet de survol subtil
        s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        color = (*Colors.ORANGE[:3], 30) if self.env.current_player == 1 else (*Colors.GREEN[:3], 30)
        s.fill(color)
        self.screen.blit(s, rect.topleft)

        # Bordure
        border_color = Colors.ORANGE_LIGHT if self.env.current_player == 1 else Colors.GREEN_LIGHT
        pygame.draw.rect(self.screen, border_color, rect, 3, border_radius=8)

    def draw_win_line(self):
        """Dessine la ligne de victoire avec animation."""
        if self.env.winner:
            color = Colors.ORANGE if self.env.winner == 1 else Colors.GREEN

            for combo in TicTacToeEnv.WINNING_COMBINATIONS:
                if all(self.env.board[i] == self.env.winner for i in combo):
                    start_cell, end_cell = combo[0], combo[2]
                    start_x = (start_cell % 3) * self.cell_size + self.cell_size // 2
                    start_y = (start_cell // 3) * self.cell_size + self.cell_size // 2
                    end_x = (end_cell % 3) * self.cell_size + self.cell_size // 2
                    end_y = (end_cell // 3) * self.cell_size + self.cell_size // 2

                    # Ligne avec effet glow
                    for width in [16, 12, 8]:
                        alpha = 100 if width == 16 else (180 if width == 12 else 255)
                        pygame.draw.line(self.screen, color, (start_x, start_y), (end_x, end_y), width)
                    break

    def draw_game_status(self):
        """Dessine la zone de statut moderne."""
        # Fond de statut semi-transparent
        status_surface = pygame.Surface((self.window_size, 120), pygame.SRCALPHA)
        status_surface.fill((255, 255, 255, 220))
        self.screen.blit(status_surface, (0, self.window_size))

        if self.env.done:
            if self.env.winner:
                # Bannière de victoire colorée
                bg_color = Colors.ORANGE if self.env.winner == 1 else Colors.GREEN
                pygame.draw.rect(self.screen, bg_color, (0, self.window_size, self.window_size, 6))

                # Grand symbole du gagnant
                symbol_y = self.window_size + 40
                if self.env.winner == 1:
                    self._draw_victory_x(self.window_size // 2 - 90, symbol_y, 22)
                else:
                    self._draw_victory_o(self.window_size // 2 - 90, symbol_y, 18)

                # Message de victoire
                message = "GAGNE !"
                color = Colors.ORANGE if self.env.winner == 1 else Colors.GREEN
                text = self.font_large.render(message, True, color)
                text_rect = text.get_rect(midleft=(self.window_size // 2 - 50, self.window_size + 40))
                self.screen.blit(text, text_rect)
            else:
                # Match nul avec style
                pygame.draw.rect(self.screen, Colors.GRAY_MEDIUM, (0, self.window_size, self.window_size, 6))

                # Dessiner X et O petits pour le nul
                self._draw_mini_x(self.window_size // 2 - 70, self.window_size + 40, 14)
                self._draw_mini_o(self.window_size // 2 - 40, self.window_size + 40, 12)

                message = "MATCH NUL"
                color = Colors.GRAY_DARK
                text = self.font_large.render(message, True, color)
                text_rect = text.get_rect(midleft=(self.window_size // 2 - 10, self.window_size + 40))
                self.screen.blit(text, text_rect)
        else:
            # Tour en cours
            border_color = Colors.ORANGE if self.env.current_player == 1 else Colors.GREEN
            pygame.draw.rect(self.screen, border_color, (0, self.window_size, self.window_size, 4))

            # Symbole du joueur actuel
            symbol_y = self.window_size + 40
            if self.env.current_player == 1:
                self._draw_mini_x(self.window_size // 2 - 90, symbol_y, 16)
                message = "À ton tour !"
                color = Colors.ORANGE
            else:
                self._draw_mini_o(self.window_size // 2 - 90, symbol_y, 13)
                message = "Tour de l'IA"
                color = Colors.GREEN

            text = self.font_large.render(message, True, color)
            text_rect = text.get_rect(midleft=(self.window_size // 2 - 60, self.window_size + 40))
            self.screen.blit(text, text_rect)

        # Instructions en bas avec meilleure lisibilité
        instructions = f"{self.game_message}  •  R: Rejouer  •  M: Menu"
        sub_text = self.font_small.render(instructions, True, Colors.TEXT_SECONDARY)
        sub_rect = sub_text.get_rect(center=(self.window_size // 2, self.window_size + 90))
        self.screen.blit(sub_text, sub_rect)

    def draw_game(self):
        """Dessine l'écran de jeu complet."""
        self.draw_grid()

        for i in range(9):
            if self.env.board[i] != 0:
                self.draw_symbol(i, self.env.board[i])

        if self.highlighted_cell is not None and not self.env.done:
            if self.highlighted_cell in self.env.legal_actions():
                self.draw_highlight(self.highlighted_cell)

        if self.env.done:
            self.draw_win_line()

        self.draw_game_status()
        pygame.display.flip()

    def draw_training_screen(self):
        """Dessine l'écran d'entraînement moderne."""
        # Fond blanc opaque pour meilleure lisibilité
        self.screen.fill(Colors.WHITE)

        # Bande décorative
        pygame.draw.rect(self.screen, Colors.GREEN, (0, 0, self.window_size, 6))

        # Titre avec fond
        title_bg = pygame.Rect(0, 20, self.window_size, 50)
        pygame.draw.rect(self.screen, Colors.GREEN, title_bg)
        title = self.font_title.render("ENTRAÎNEMENT", True, Colors.WHITE)
        title_rect = title.get_rect(center=(self.window_size // 2, 45))
        self.screen.blit(title, title_rect)

        # Zone de progression avec fond blanc solide
        progress_rect = pygame.Rect(20, 85, self.window_size - 40, self.window_height - 150)
        pygame.draw.rect(self.screen, Colors.BACKGROUND_SOFT, progress_rect, border_radius=8)
        pygame.draw.rect(self.screen, Colors.GREEN, progress_rect, 2, border_radius=8)

        # Afficher la progression avec police plus grande
        lines = self.training_progress.split('\n')
        y = 105
        for line in lines[-10:]:
            if "Win:" in line or "Victoires" in line:
                color = Colors.GREEN_DARK
                font = self.font_medium
            elif "Episode" in line:
                color = Colors.ORANGE
                font = self.font_medium
            elif "Resultats" in line or "EVALUATION" in line:
                color = Colors.GREEN_DARK
                font = self.font_medium
            else:
                color = Colors.TEXT_PRIMARY
                font = self.font_small
            text = font.render(line, True, color)
            self.screen.blit(text, (35, y))
            y += 32

        # Instructions en bas
        help_bg = pygame.Rect(0, self.window_height - 45, self.window_size, 45)
        pygame.draw.rect(self.screen, Colors.GREEN_LIGHT, help_bg)
        help_text = self.font_medium.render("M: Retour au menu", True, Colors.WHITE)
        help_rect = help_text.get_rect(center=(self.window_size // 2, self.window_height - 22))
        self.screen.blit(help_text, help_rect)

        pygame.display.flip()

    def get_cell_from_pos(self, pos: Tuple[int, int]) -> Optional[int]:
        x, y = pos
        if y > self.window_size:
            return None
        col = x // self.cell_size
        row = y // self.cell_size
        if 0 <= row < 3 and 0 <= col < 3:
            return row * 3 + col
        return None

    def is_human_turn(self) -> bool:
        if self.mode == GameMode.HUMAN_VS_HUMAN:
            return True
        elif self.mode == GameMode.HUMAN_VS_AI:
            return self.env.current_player == 1
        return False

    def ai_move(self):
        if self.agent is None or self.env.done:
            return

        current_time = pygame.time.get_ticks()
        if current_time - self.last_ai_move_time < self.ai_delay:
            return

        state_key = self.env.get_state_key()
        legal_actions = self.env.legal_actions()

        if legal_actions:
            action = self.agent.choose_action(state_key, legal_actions, training=False)
            self.env.step(action)
            self.last_ai_move_time = current_time

    def handle_game_click(self, pos: Tuple[int, int]):
        if self.env.done or not self.is_human_turn():
            return

        cell = self.get_cell_from_pos(pos)
        if cell is not None and cell in self.env.legal_actions():
            self.env.step(cell)

    def start_game(self, mode: GameMode):
        self.mode = mode
        self.env.reset()

        if mode == GameMode.HUMAN_VS_HUMAN:
            self.game_message = "Humain vs Humain"
        elif mode == GameMode.HUMAN_VS_AI:
            if not self.load_agent():
                self.run_training(quick=True)
            self.game_message = "Humain vs IA"
        elif mode == GameMode.AI_VS_AI:
            if not self.load_agent():
                self.run_training(quick=True)
            self.game_message = "IA vs IA"
            self.ai_delay = 700

    def run_training(self, quick: bool = False):
        self.mode = GameMode.TRAINING
        self.is_processing = True
        self.training_progress = "Initialisation...\n"
        self.draw_training_screen()
        pygame.display.flip()

        # Plus d'épisodes pour une IA plus forte
        num_episodes = 30000 if quick else 100000
        log_interval = num_episodes // 10

        self.agent = QLearningAgent(
            alpha=0.2,          # Learning rate plus élevé
            gamma=0.95,         # Discount factor
            epsilon=1.0,
            epsilon_min=0.05,   # Garder un peu d'exploration
            epsilon_decay=0.99995,  # Décroissance plus lente
            player=1
        )

        trainer = Trainer(self.agent)
        self.training_progress += f"Episodes: {num_episodes} (X et O)\n"
        self.training_progress += f"Parametres: alpha=0.2, gamma=0.95\n\n"

        wins = 0
        for episode in range(1, num_episodes + 1):
            # Alterner entre jouer X (1) et O (2) pour apprendre les deux rôles
            play_as = 1 if episode % 2 == 1 else 2
            reward, winner = trainer.train_episode(agent_plays_as=play_as)
            if winner == play_as:
                wins += 1

            if episode % log_interval == 0:
                win_rate = wins / episode * 100
                self.training_progress += f"Episode {episode:6d} | Win: {win_rate:.1f}% | eps: {self.agent.epsilon:.4f}\n"
                self.draw_training_screen()
                pygame.event.pump()

        self.training_progress += "\nEvaluation (200 parties)...\n"
        self.draw_training_screen()
        pygame.event.pump()

        results = trainer.evaluate(num_games=200, verbose=False)
        self.training_progress += f"\nResultats finaux:\n"
        self.training_progress += f"  Victoires: {results['wins']} ({results['win_rate']:.1f}%)\n"
        self.training_progress += f"  Defaites: {results['losses']} ({results['loss_rate']:.1f}%)\n"
        self.training_progress += f"  Nuls: {results['draws']} ({results['draw_rate']:.1f}%)\n"

        self.agent.save(self.DEFAULT_AGENT_PATH)
        self.training_progress += f"\nAgent sauvegarde!\n"

        self.is_processing = False
        self.agent.epsilon = 0.0

    def run_evaluation(self):
        self.mode = GameMode.EVALUATION
        self.training_progress = "EVALUATION DE L'AGENT\n\n"

        if not self.load_agent():
            self.training_progress += "Aucun agent trouve!\n"
            self.training_progress += "Entrainez d'abord un agent.\n"
            return

        self.training_progress += f"Agent charge: {self.agent.get_stats()['q_table_size']} etats\n"
        self.training_progress += f"Episodes d'entrainement: {self.agent.training_episodes}\n\n"
        self.training_progress += "Evaluation sur 200 parties...\n"
        self.draw_training_screen()
        pygame.event.pump()

        trainer = Trainer(self.agent)
        results = trainer.evaluate(num_games=200, verbose=False)

        self.training_progress += f"\nResultats:\n"
        self.training_progress += f"  Victoires: {results['wins']} ({results['win_rate']:.1f}%)\n"
        self.training_progress += f"  Defaites: {results['losses']} ({results['loss_rate']:.1f}%)\n"
        self.training_progress += f"  Nuls: {results['draws']} ({results['draw_rate']:.1f}%)\n"

    def run(self):
        """Boucle principale."""
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.mode == GameMode.MENU:
                            running = False
                        else:
                            self.mode = GameMode.MENU

                    elif event.key == pygame.K_m:
                        self.mode = GameMode.MENU

                    elif event.key == pygame.K_r and self.mode in [GameMode.HUMAN_VS_HUMAN, GameMode.HUMAN_VS_AI, GameMode.AI_VS_AI]:
                        self.env.reset()

                elif event.type == pygame.MOUSEMOTION:
                    if self.mode == GameMode.MENU:
                        for btn in self.menu_buttons:
                            btn.update_hover(event.pos)
                    else:
                        self.highlighted_cell = self.get_cell_from_pos(event.pos)

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.mode == GameMode.MENU:
                        for btn in self.menu_buttons:
                            if btn.is_clicked(event.pos):
                                if btn.mode == GameMode.TRAINING:
                                    self.run_training()
                                elif btn.mode == GameMode.EVALUATION:
                                    self.run_evaluation()
                                else:
                                    self.start_game(btn.mode)
                    elif self.mode in [GameMode.HUMAN_VS_HUMAN, GameMode.HUMAN_VS_AI]:
                        self.handle_game_click(event.pos)

            if self.mode in [GameMode.HUMAN_VS_AI, GameMode.AI_VS_AI]:
                if not self.is_human_turn() and not self.env.done:
                    self.ai_move()

            if self.mode == GameMode.MENU:
                self.draw_menu()
            elif self.mode in [GameMode.HUMAN_VS_HUMAN, GameMode.HUMAN_VS_AI, GameMode.AI_VS_AI]:
                self.draw_game()
            elif self.mode in [GameMode.TRAINING, GameMode.EVALUATION]:
                self.draw_training_screen()

            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    gui = PygameGUI()
    gui.run()
