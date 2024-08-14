
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