from flask import Blueprint, render_template, request
from app.cricket.models import Match, FantasyTeam, Team
from app.cricket.forms import MatchForm
from datetime import datetime
from app.extensions import db


game = Blueprint("game", __name__, template_folder="templates")


@game.route("/", methods=["GET", "POST"])
def main():
    form = MatchForm()
    context = {"form": form}
    if form.validate_on_submit():
        home_team = request.form.get("home_team")
        away_team = request.form.get("away_team")
        if home_team and away_team:
            # match = Match(Team.CSK, Team.PBKS)
            match = Match(home_team, away_team)
            result = match.get_fantasy_teams()
            context["result"] = result
    # return render_template("cricket/teams.html")
    return render_template("cricket/index.html", **context)


@game.route("/data")
def data():
    query = FantasyTeam.query

    # search filter
    search = request.args.get("search")

    if search:
        query = query.filter(
            db.or_(
                FantasyTeam.player1.like(f"%{search}%"),
                FantasyTeam.player2.like(f"%{search}%"),
                FantasyTeam.player3.like(f"%{search}%"),
                FantasyTeam.player4.like(f"%{search}%"),
                FantasyTeam.player5.like(f"%{search}%"),
                FantasyTeam.player6.like(f"%{search}%"),
                FantasyTeam.player7.like(f"%{search}%"),
                FantasyTeam.player8.like(f"%{search}%"),
                FantasyTeam.player9.like(f"%{search}%"),
                FantasyTeam.player10.like(f"%{search}%"),
                FantasyTeam.player11.like(f"%{search}%"),
                FantasyTeam.credits.like(f"%{search}%"),
            )
        )
    total = query.count()

    # sorting
    sort = request.args.get("sort")
    if sort:
        order = []
        for s in sort.split(","):
            direction = s[0]
            name = s[1:]
            if name not in [
                "player1",
                "player2",
                "player3",
                "player4",
                "player5",
                "player6",
                "player7",
                "player8",
                "player9",
                "player10",
                "player11",
            ]:
                name = "credits"
            col = getattr(FantasyTeam, name)
            if direction == "-":
                col = col.desc()
            order.append(col)
        if order:
            query = query.order_by(*order)

    # pagination
    start = request.args.get("start", type=int, default=-1)
    length = request.args.get("length", type=int, default=-1)
    if start != -1 and length != -1:
        query = query.offset(start).limit(length)

    # response
    return {
        "data": [team.to_dict() for team in query],
        "total": total,
    }
