"""
Module Entraînement - Boucle d'entraînement Q-Learning pour le Morpion
Gère les épisodes d'entraînement, les statistiques et l'évaluation.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from collections import deque
import time

from environment import TicTacToeEnv
from agent import QLearningAgent, RandomAgent


class Trainer:
    """
    Classe d'entraînement pour l'agent Q-Learning.

    Gère:
    - La boucle d'entraînement (épisodes)
    - Le suivi des statistiques (victoires, défaites, nuls)
    - L'évaluation contre un agent aléatoire
    """

    def __init__(
        self,
        agent: QLearningAgent,
        opponent: Optional[QLearningAgent] = None,
        env: Optional[TicTacToeEnv] = None
    ):
        """
        Initialise le trainer.

        Args:
            agent: L'agent Q-Learning à entraîner
            opponent: L'adversaire (RandomAgent par défaut)
            env: L'environnement de jeu (créé si non fourni)
        """
        self.agent = agent
        self.opponent = opponent if opponent else RandomAgent(player=2)
        self.env = env if env else TicTacToeEnv()

        # Statistiques d'entraînement
        self.wins = 0
        self.losses = 0
        self.draws = 0
        self.episode_rewards: List[float] = []
        self.win_rates: List[float] = []

    def train_episode(self, agent_plays_as: int = 1) -> Tuple[float, int]:
        """
        Exécute un épisode d'entraînement complet.

        Args:
            agent_plays_as: Le joueur que l'agent incarne (1 ou 2)

        Returns:
            Tuple (récompense finale pour l'agent, gagnant: 1, 2, ou 0 pour nul)
        """
        self.env.reset()
        done = False

        # Historique des transitions pour l'agent (pour mise à jour rétroactive)
        agent_transitions: List[Tuple[tuple, int, float, tuple, List[int], bool]] = []

        while not done:
            state_key = self.env.get_state_key()
            legal_actions = self.env.legal_actions()
            current_player = self.env.current_player

            if current_player == agent_plays_as:
                # Tour de l'agent
                action = self.agent.choose_action(state_key, legal_actions, training=True)
                next_state, reward, done = self.env.step(action)
                next_state_key = self.env.get_state_key()
                next_legal = self.env.legal_actions()

                # Ajuster la récompense pour le joueur 2
                if done and self.env.winner == agent_plays_as:
                    reward = 1.0

                # Stocker la transition
                agent_transitions.append((state_key, action, reward, next_state_key, next_legal, done))

            else:
                # Tour de l'adversaire (random)
                action = self.opponent.choose_action(state_key, legal_actions, training=True)
                next_state, reward, done = self.env.step(action)

                # Si l'adversaire gagne, mettre à jour la dernière transition de l'agent avec récompense négative
                opponent_player = 3 - agent_plays_as
                if done and self.env.winner == opponent_player:
                    if agent_transitions:
                        last = agent_transitions[-1]
                        # Remplacer avec récompense -1 pour la défaite
                        agent_transitions[-1] = (last[0], last[1], -1.0, last[3], last[4], True)

        # Appliquer l'apprentissage sur toutes les transitions de l'agent
        for transition in agent_transitions:
            self.agent.learn(*transition)

        # Decay epsilon
        self.agent.decay_epsilon()

        # Mettre à jour les statistiques
        final_reward = self.env.get_reward_for_player(agent_plays_as)
        if self.env.winner == agent_plays_as:
            self.wins += 1
        elif self.env.winner is not None:
            self.losses += 1
        else:
            self.draws += 1

        return final_reward, self.env.winner if self.env.winner else 0

    def train(
        self,
        num_episodes: int = 10000,
        verbose: bool = True,
        log_interval: int = 1000
    ) -> Dict:
        """
        Entraîne l'agent sur plusieurs épisodes.

        Args:
            num_episodes: Nombre d'épisodes d'entraînement
            verbose: Afficher la progression
            log_interval: Intervalle d'affichage des statistiques

        Returns:
            Dictionnaire avec les statistiques d'entraînement
        """
        start_time = time.time()

        # Reset des statistiques
        self.wins = 0
        self.losses = 0
        self.draws = 0
        self.episode_rewards = []
        recent_results = deque(maxlen=log_interval)

        if verbose:
            print(f"Début de l'entraînement: {num_episodes} épisodes")
            print(f"Hyperparamètres: α={self.agent.alpha}, γ={self.agent.gamma}, "
                  f"ε={self.agent.epsilon:.4f} → {self.agent.epsilon_min}")
            print("-" * 60)

        for episode in range(1, num_episodes + 1):
            reward, winner = self.train_episode()
            self.episode_rewards.append(reward)
            recent_results.append(1 if winner == self.agent.player else 0)

            if verbose and episode % log_interval == 0:
                win_rate = sum(recent_results) / len(recent_results) * 100
                self.win_rates.append(win_rate)
                elapsed = time.time() - start_time
                print(f"Épisode {episode:6d} | "
                      f"Win rate (derniers {log_interval}): {win_rate:5.1f}% | "
                      f"ε: {self.agent.epsilon:.4f} | "
                      f"Q-table: {len(self.agent.q_table):6d} | "
                      f"Temps: {elapsed:.1f}s")

        total_time = time.time() - start_time

        stats = {
            'episodes': num_episodes,
            'wins': self.wins,
            'losses': self.losses,
            'draws': self.draws,
            'final_epsilon': self.agent.epsilon,
            'q_table_size': len(self.agent.q_table),
            'training_time': total_time,
            'win_rates': self.win_rates
        }

        if verbose:
            print("-" * 60)
            print(f"Entraînement terminé en {total_time:.1f}s")
            print(f"Résultats: {self.wins} victoires, {self.losses} défaites, {self.draws} nuls")
            print(f"Taux de victoire global: {self.wins / num_episodes * 100:.1f}%")

        return stats

    def evaluate(
        self,
        num_games: int = 200,
        opponent: Optional[RandomAgent] = None,
        verbose: bool = True
    ) -> Dict:
        """
        Évalue l'agent contre un adversaire (mode greedy, epsilon=0).

        Args:
            num_games: Nombre de parties d'évaluation
            opponent: Adversaire pour l'évaluation (RandomAgent par défaut)
            verbose: Afficher les résultats

        Returns:
            Dictionnaire avec les résultats d'évaluation
        """
        if opponent is None:
            opponent = RandomAgent(player=2)

        wins = 0
        losses = 0
        draws = 0

        # Sauvegarder epsilon et le mettre à 0 pour l'évaluation
        original_epsilon = self.agent.epsilon
        self.agent.epsilon = 0.0

        for _ in range(num_games):
            self.env.reset()
            done = False

            while not done:
                state_key = self.env.get_state_key()
                legal_actions = self.env.legal_actions()

                if self.env.current_player == self.agent.player:
                    action = self.agent.choose_action(state_key, legal_actions, training=False)
                else:
                    action = opponent.choose_action(state_key, legal_actions)

                _, _, done = self.env.step(action)

            if self.env.winner == self.agent.player:
                wins += 1
            elif self.env.winner == opponent.player:
                losses += 1
            else:
                draws += 1

        # Restaurer epsilon
        self.agent.epsilon = original_epsilon

        win_rate = wins / num_games * 100
        loss_rate = losses / num_games * 100
        draw_rate = draws / num_games * 100

        results = {
            'games': num_games,
            'wins': wins,
            'losses': losses,
            'draws': draws,
            'win_rate': win_rate,
            'loss_rate': loss_rate,
            'draw_rate': draw_rate
        }

        if verbose:
            print(f"\n=== Évaluation ({num_games} parties) ===")
            print(f"Victoires: {wins} ({win_rate:.1f}%)")
            print(f"Défaites:  {losses} ({loss_rate:.1f}%)")
            print(f"Nuls:      {draws} ({draw_rate:.1f}%)")

        return results


def train_and_save(
    save_path: str = "agent_trained.pkl",
    num_episodes: int = 50000,
    evaluate_after: bool = True
) -> QLearningAgent:
    """
    Fonction utilitaire pour entraîner et sauvegarder un agent.

    Args:
        save_path: Chemin de sauvegarde
        num_episodes: Nombre d'épisodes d'entraînement
        evaluate_after: Évaluer après l'entraînement

    Returns:
        L'agent entraîné
    """
    agent = QLearningAgent(
        alpha=0.1,
        gamma=0.99,
        epsilon=1.0,
        epsilon_min=0.01,
        epsilon_decay=0.9995,
        player=1
    )

    trainer = Trainer(agent)
    trainer.train(num_episodes=num_episodes)

    if evaluate_after:
        trainer.evaluate(num_games=200)

    agent.save(save_path)
    return agent


# Test unitaire
if __name__ == "__main__":
    print("=== Test du module d'entraînement ===\n")

    # Créer un agent et un trainer
    agent = QLearningAgent(
        alpha=0.1,
        gamma=0.99,
        epsilon=1.0,
        epsilon_min=0.1,
        epsilon_decay=0.995,
        player=1
    )

    trainer = Trainer(agent)

    # Entraînement court pour le test
    print("Entraînement de test (1000 épisodes)...")
    stats = trainer.train(num_episodes=1000, log_interval=200)

    # Évaluation
    results = trainer.evaluate(num_games=100)

    print(f"\nStatistiques finales:")
    print(f"  - Taille Q-table: {agent.get_stats()['q_table_size']}")
    print(f"  - Epsilon final: {agent.epsilon:.4f}")
