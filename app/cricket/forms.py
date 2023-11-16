from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from app.cricket.models import Team
from app.utils import get_attrs


def get_teams():
    team_choices = []
    teams = get_attrs(Team)
    for team in teams:
        words = team.split(" ")
        item = ""
        for word in words:
            item += word[0]
        team_choices.append((item, team))
    return team_choices


def get_choices():
    return [(team, team) for team in get_attrs(Team)]


CHOICES = get_choices()


class MatchForm(FlaskForm):
    home_team = SelectField(label='Home Team', choices=CHOICES)
    away_team = SelectField(label='Away Team', choices=CHOICES)
    submit = SubmitField("Submit")
