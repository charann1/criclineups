from instance import settings
from itertools import chain, combinations, product
from app.extensions import db

# import sys


class Game:
    def __init__(self, match):
        self.match = match

    @staticmethod
    def patterns(wicket_keepers, batsmens, all_rounders, bowlers):
        return Game.__patterns(wicket_keepers, batsmens, all_rounders, bowlers)

    @staticmethod
    def __patterns(wicket_keepers, batsmens, all_rounders, bowlers):
        MAX_WICKET_KEEPERS = (
            (settings.MAX_WICKET_KEEPERS + 1)
            if settings.MAX_WICKET_KEEPERS <= wicket_keepers
            else (wicket_keepers + 1)
        )

        MAX_BATSMENS = (
            (settings.MAX_BATSMENS + 1)
            if settings.MAX_BATSMENS <= batsmens
            else (batsmens + 1)
        )

        MAX_ALL_ROUNDERS = (
            (settings.MAX_ALL_ROUNDERS + 1)
            if settings.MAX_ALL_ROUNDERS <= all_rounders
            else (all_rounders + 1)
        )

        MAX_BOWLERS = (
            (settings.MAX_BOWLERS + 1)
            if settings.MAX_BOWLERS <= bowlers
            else (bowlers + 1)
        )

        patterns = product(
            range(settings.MIN_WICKET_KEEPERS, MAX_WICKET_KEEPERS),
            range(settings.MIN_BATSMENS, MAX_BATSMENS),
            range(settings.MIN_ALL_ROUNDERS, MAX_ALL_ROUNDERS),
            range(settings.MIN_BOWLERS, MAX_BOWLERS),
        )

        possible_patterns = [
            pattern for pattern in patterns if sum(pattern) == settings.MAX_PLAYERS
        ]

        return possible_patterns

    @staticmethod
    def __filter(home_team, away_team, fantasy_team, pattern, team):
        total_points = 0
        total_credits = 0
        home_team_players = 0
        away_team_players = 0

        players = list(chain.from_iterable(fantasy_team))

        for player in players:
            # total_points += player.points
            total_credits += player.credits

            if player.team == home_team:
                home_team_players += 1
            elif player.team == away_team:
                away_team_players += 1

        # Checking conditions
        if total_credits <= settings.MAX_CREDITS:
            if (
                home_team_players >= settings.MIN_HOME_TEAM_PLAYERS
                and home_team_players <= settings.MAX_HOME_TEAM_PLAYERS
            ):
                if (
                    away_team_players >= settings.MIN_AWAY_TEAM_PLAYERS
                    and away_team_players <= settings.MAX_AWAY_TEAM_PLAYERS
                ):
                    return team(
                        player1=players[0].name,
                        player2=players[1].name,
                        player3=players[2].name,
                        player4=players[3].name,
                        player5=players[4].name,
                        player6=players[5].name,
                        player7=players[6].name,
                        player8=players[7].name,
                        player9=players[8].name,
                        player10=players[9].name,
                        player11=players[10].name,
                        points=total_points,
                        credits=total_credits,
                        wicket_keepers=pattern[0],
                        batsmens=pattern[1],
                        all_rounders=pattern[2],
                        bowlers=pattern[3],
                        home_team_players=home_team_players,
                        away_team_players=away_team_players,
                    )
        return None

    def possible_teams(self):
        return self.__possible_teams()

    def __possible_teams(self):
        from app.cricket.models import FantasyTeam

        FantasyTeam.query.delete()
        # fantasy_teams = []

        home_team = self.match.home_team
        away_team = self.match.away_team

        self.match.update_players()

        wicket_keepers = self.match.wicket_keepers
        batsmens = self.match.batsmens
        all_rounders = self.match.all_rounders
        bowlers = self.match.bowlers

        possible_patterns = Game.patterns(
            len(wicket_keepers), len(batsmens), len(all_rounders), len(bowlers)
        )

        for pattern in possible_patterns:
            wicket_keeper_combinations = list(combinations(wicket_keepers, pattern[0]))

            batsmen_combinations = list(combinations(batsmens, pattern[1]))

            all_rounder_combinations = list(combinations(all_rounders, pattern[2]))

            bowler_combinations = list(combinations(bowlers, pattern[3]))

            _fantasy_teams = product(
                wicket_keeper_combinations,
                batsmen_combinations,
                all_rounder_combinations,
                bowler_combinations,
            )

            _fantasy_teams = list(
                map(
                    lambda fantasy_team: Game.__filter(
                        home_team, away_team, fantasy_team, pattern, FantasyTeam
                    ),
                    _fantasy_teams,
                )
            )

            fantasy_teams = [
                fantasy_team for fantasy_team in _fantasy_teams if fantasy_team
            ]

            db.session.bulk_save_objects(fantasy_teams)

        # print(sys.getsizeof(fantasy_teams))

        # FantasyTeam.query.delete()
        # db.session.bulk_save_objects(fantasy_teams)
        db.session.commit()

        return len(fantasy_teams)


if __name__ == "__main__":
    pass
