NPM28 IS NO GO


pixel short id: 2016815973
private movie id: 33086760

code, resp = invoke_method(
    SERVER,
    "Moviestarplanet.WebService.MovieService.AMFMovieService.MovieWatched",
    [
        ticket_header(ticket),
        33086440,
        actor_id
    ],
    get_session_id()
)

code, resp = invoke_method(
    SERVER,
    "Moviestarplanet.WebService.MovieService.AMFMovieService.RateMovie",
    [
        ticket_header(ticket),
        {
            "ActorId" : actor_id,
            "RateMovieId" : 0,
            "RateDate" : datetime.now(),
            "MovieId" : 33086440,
            "Comment" : "",
            "Score" : 5
        }
    ],
    get_session_id()
)

code, resp = invoke_method(
    SERVER,
    "MovieStarPlanet.WebService.UserSession.AMFUserSessionService.GiveAutographAndCalculateTimestamp",
    [
        ticket_header(ticket),
        actor_id,
        friend_actor
    ],
    get_session_id()
)


code, resp = invoke_method(
    SERVER,
    "MovieStarPlanet.WebService.UserSession.AMFUserSessionService.GetActorIdFromName",
    [
        "starwarfare123"
    ],
    get_session_id()
)