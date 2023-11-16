from app.extensions import db
from app.utils import get_attrs
from app.cricket.game import Game


class Country:
    AFG = "Afghanistan"
    AUS = "Australia"
    BAN = "Bangladesh"
    ENG = "England"
    IND = "India"
    PAK = "Pakistan"
    NZ = "New Zealand"
    SA = "South Africa"
    SL = "Sri Lanka"
    WI = "West Indies"


class Team:
    CSK = "Chennai Super Kings"
    DC = "Delhi Capitals"
    GT = "Gujarat Titans"
    KKR = "Kolkata Knight Riders"
    LSG = "Lucknow Super Giants"
    MI = "Mumbai Indians"
    PBKS = "Punjab Kings"
    RR = "Rajasthan Royals"
    RCB = "Royal Challengers Bangalore"
    SRH = "Sun Risers Hyderabad"


class PlayerType:
    IN = "Indian"
    FN = "Foreign"


class PlayerStatus:
    IN = "Playing"
    OUT = "Bench"


class PlayerKind:
    AR = "ALL ROUNDER"
    BAT = "BATSMEN"
    BOW = "BOWLER"
    WK = "WICKET KEEPER"


class FantasyPlayer(db.Model):
    __tablename__ = 'fantasy_players'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    country = db.Column(db.String(60), nullable=False)
    team = db.Column(db.String(60), nullable=False)
    type = db.Column(db.String(60), nullable=False)
    kind = db.Column(db.String(60), nullable=False)
    points = db.Column(db.Float, nullable=False)
    credits = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(10), nullable=False, default=PlayerStatus.OUT)

    def __init__(self, name, country, team, type, kind, points, credits, status):

        self.name = name
        self.country = country
        self.team = team
        self.type = type
        self.kind = kind
        self.points = points
        self.credits = credits
        self.status = status

    def __repr__(self):
        return self.name


class Match:
    id = db.Column(db.Integer, primary_key=True)
    home_team = db.Column(db.String(256), nullable=False)
    away_team = db.Column(db.String(256), nullable=False)

    def __init__(self, home_team, away_team):
        self.home_team = home_team
        self.away_team = away_team
        self.__wicket_keepers = None
        self.__batsmens = None
        self.__all_rounders = None
        self.__bowlers = None
        self.update_players()

    @property
    def title(self):
        return "{} vs {}".format(self.home_team, self.away_team)

    @property
    def wicket_keepers(self):
        return self.__wicket_keepers

    @property
    def batsmens(self):
        return self.__batsmens

    @property
    def all_rounders(self):
        return self.__all_rounders

    @property
    def bowlers(self):
        return self.__bowlers

    def update_players(self):
        self.__update_wicket_keepers()
        self.__update_batsmens()
        self.__update_all_rounders()
        self.__update_bowlers()

    def __update_wicket_keepers(self):
        _wicket_keepers = FantasyPlayer.query\
            .filter(FantasyPlayer.kind == PlayerKind.WK)\
            .filter(FantasyPlayer.status == PlayerStatus.IN)\
            .filter((FantasyPlayer.team == self.home_team) | (FantasyPlayer.team == self.away_team))\
            .all()
        self.__wicket_keepers = _wicket_keepers

    def __update_batsmens(self):
        _batsmens = FantasyPlayer.query\
            .filter(FantasyPlayer.kind == PlayerKind.BAT)\
            .filter(FantasyPlayer.status == PlayerStatus.IN)\
            .filter((FantasyPlayer.team == self.home_team) | (FantasyPlayer.team == self.away_team))\
            .all()
        self.__batsmens = _batsmens

    def __update_all_rounders(self):
        _all_rounders = FantasyPlayer.query\
            .filter(FantasyPlayer.kind == PlayerKind.AR)\
            .filter(FantasyPlayer.status == PlayerStatus.IN)\
            .filter((FantasyPlayer.team == self.home_team) | (FantasyPlayer.team == self.away_team))\
            .all()
        self.__all_rounders = _all_rounders

    def __update_bowlers(self):
        _bowlers = FantasyPlayer.query\
            .filter(FantasyPlayer.kind == PlayerKind.BOW)\
            .filter(FantasyPlayer.status == PlayerStatus.IN)\
            .filter((FantasyPlayer.team == self.home_team) | (FantasyPlayer.team == self.away_team))\
            .all()
        self.__bowlers = _bowlers

    def get_fantasy_teams(self):
        return self.__fantasy_teams()

    def __fantasy_teams(self):
        game = Game(self)
        return game.possible_teams()

    def __repr__(self):
        return "Match : " + self.title


class FantasyTeam(db.Model):
    __tablename__ = 'fantasy_teams'

    id = db.Column(db.Integer, primary_key=True)
    player1 = db.Column(db.String(128), db.ForeignKey("fantasy_players.name"))
    player2 = db.Column(db.String(128), db.ForeignKey("fantasy_players.name"))
    player3 = db.Column(db.String(128), db.ForeignKey("fantasy_players.name"))
    player4 = db.Column(db.String(128), db.ForeignKey("fantasy_players.name"))
    player5 = db.Column(db.String(128), db.ForeignKey("fantasy_players.name"))
    player6 = db.Column(db.String(128), db.ForeignKey("fantasy_players.name"))
    player7 = db.Column(db.String(128), db.ForeignKey("fantasy_players.name"))
    player8 = db.Column(db.String(128), db.ForeignKey("fantasy_players.name"))
    player9 = db.Column(db.String(128), db.ForeignKey("fantasy_players.name"))
    player10 = db.Column(db.String(128), db.ForeignKey("fantasy_players.name"))
    player11 = db.Column(db.String(128), db.ForeignKey("fantasy_players.name"))
    player_1 = db.relationship("FantasyPlayer", foreign_keys=[player1])
    player_2 = db.relationship("FantasyPlayer", foreign_keys=[player2])
    player_3 = db.relationship("FantasyPlayer", foreign_keys=[player3])
    player_4 = db.relationship("FantasyPlayer", foreign_keys=[player4])
    player_5 = db.relationship("FantasyPlayer", foreign_keys=[player5])
    player_6 = db.relationship("FantasyPlayer", foreign_keys=[player6])
    player_7 = db.relationship("FantasyPlayer", foreign_keys=[player7])
    player_8 = db.relationship("FantasyPlayer", foreign_keys=[player8])
    player_9 = db.relationship("FantasyPlayer", foreign_keys=[player9])
    player_10 = db.relationship("FantasyPlayer", foreign_keys=[player10])
    player_11 = db.relationship("FantasyPlayer", foreign_keys=[player11])
    credits = db.Column(db.Float, nullable=False)
    points = db.Column(db.Float, nullable=False)
    wicket_keepers = db.Column(db.Integer, nullable=False)
    batsmens = db.Column(db.Integer, nullable=False)
    all_rounders = db.Column(db.Integer, nullable=False)
    bowlers = db.Column(db.Integer, nullable=False)
    home_team_players = db.Column(db.Integer, nullable=False)
    away_team_players = db.Column(db.Integer, nullable=False)

    def __init__(self, player1, player2, player3, player4, player5, player6, player7, player8, player9, player10, player11, points, credits, wicket_keepers, batsmens, all_rounders, bowlers, home_team_players, away_team_players):
        self.player1 = player1
        self.player2 = player2
        self.player3 = player3
        self.player4 = player4
        self.player5 = player5
        self.player6 = player6
        self.player7 = player7
        self.player8 = player8
        self.player9 = player9
        self.player10 = player10
        self.player11 = player11
        self.points = points
        self.credits = credits
        self.wicket_keepers = wicket_keepers
        self.batsmens = batsmens
        self.all_rounders = all_rounders
        self.bowlers = bowlers
        self.home_team_players = home_team_players
        self.away_team_players = away_team_players

    def to_dict(self):
        return {
            'id': self.id,
            # "players": f"{self.player1}, {self.player2}, {self.player3}, {self.player4}, {self.player5}, {self.player6}, {self.player7}, {self.player8}, {self.player9}, {self.player10}, {self.player11}",
            "player1": self.player1,
            "player2": self.player2,
            "player3": self.player3,
            "player4": self.player4,
            "player5": self.player5,
            "player6": self.player6,
            "player7": self.player7,
            "player8": self.player8,
            "player9": self.player9,
            "player10": self.player10,
            "player11": self.player11,
            "credits": self.credits,
        }

    def get_players(self):
        return [
            self.player_1, self.player_2, self.player_3, self.player_4, self.player_5,
            self.player_6, self.player_7, self.player_8, self.player_9, self.player_10, self.player_11
        ]

    def __get_string(self):
        players = self.get_players()

        names = [player.name for player in players]
        n = len(max(names, key=len)) if len(max(names, key=len)
                                            ) > len("PLAYER") else len("PLAYER")
        teams = []
        [
            teams.append(player.team)
            for player in players if player.team not in teams
        ]
        t = len(max(teams, key=len)) if len(max(teams, key=len)
                                            ) > len("TEAM") else len("TEAM")
        kinds = get_attrs(PlayerKind)
        k = len(max(kinds, key=len)) if len(max(kinds, key=len)
                                            ) > len("KIND") else len("KIND")
        points = [str(player.credits) for player in players]
        c = len(max(points, key=len)) if len(max(points, key=len)
                                             ) > len("CREDITS") else len("CREDITS")
        i = len(str(len(players)))

        string = "\n{}".format(((sum([i, n, t, k, c])+26) * "-"))
        string += "\n|  ""{}  |  PLAYER{}  |  TEAM{}  |  KIND{}  |  CREDITS{}  |".format(
            (i - len("")) * " ",
            (n - len("PLAYER")) * " ",
            (t - len("TEAM")) * " ",
            (k - len("KIND")) * " ",
            (c - len("CREDITS")) * " "

        )
        string += "\n{}".format(((sum([i, n, t, k, c])+26) * "-"))

        index = 1
        for player in players:
            index_len = (i - len(str(index))) * " "
            name = player.name
            name_len = (n - len(name)) * " "
            team = player.team
            team_len = (t - len(team)) * " "
            kind = player.kind
            kind_len = (k - len(kind)) * " "
            crs = player.credits
            crs_len = (c - len(str(crs))) * " "
            string += "\n|  {0}{1}  |  {2}{3}  |  {4}{5}  |  {6}{7}  |  {8}{9}  |".format(
                index, index_len,
                name, name_len,
                team, team_len,
                kind, kind_len,
                crs, crs_len
            )
            index += 1
            string += "\n{}".format(((sum([i, n, t, k, c])+26) * "-"))

        string += "\nWK : {0}  |  BAT : {1}  |  AR : {2}  |  BOW: {3}  |  Home : {4}  | Away : {5}  |  Credits : {6}".format(
            self.wicket_keepers,
            self.batsmens,
            self.all_rounders,
            self.bowlers,
            self.home_team_players,
            self.away_team_players,
            self.credits,
        )
        string += "\n{}".format(((sum([i, n, t, k, c])+26) * "-"))
        return string

    def __repr__(self):
        return self.__get_string()


if __name__ == "__main__":
    pass
