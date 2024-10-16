"""File containing the classes and functions to interact with the database"""

AT_LEAST = "at_least"
AT_MOST = "at_most"
CHARACTERISTICS = "characteristics="
NOT = "not"
OR = "or"
AND = "and"
EQUAL = "="

InvalidRule = Exception("Invalid Rule")


class Movie:
    def __init__(self, arr):
        self.title = arr[0]
        self.year = arr[1]
        self.genre = arr[2]
        self.duration = arr[3]
        self.country = arr[4]
        self.director = arr[5]
        self.humor = arr[6]
        self.rhythm = arr[7]
        self.effort = arr[8]
        self.tension = arr[9]
        self.vote = arr[10]
        self.votes_total = arr[11]

    def insert_to_db(self, cursor):
        cursor.execute(
            "INSERT INTO movies VALUES (?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(title) DO NOTHING",
            (
                self.title,
                self.year,
                self.genre,
                self.duration,
                self.country,
                self.director,
                self.humor,
                self.rhythm,
                self.effort,
                self.tension,
                self.vote,
                self.votes_total,
            ),
        )

    # Implement the __getitem__ method to enable index-style access
    def __getitem__(self, key):
        # Use the `getattr` function to retrieve the attribute
        return getattr(self, key)


class PastScreening:
    def __init__(self, arr):
        self.week = arr[0]
        self.day = arr[1]
        self.room = arr[2]
        self.screening = arr[3]
        self.movie = arr[4]

    def insert_to_db(self, cursor):
        cursor.execute(
            """INSERT INTO past_screenings VALUES (?,?,?,?,?) 
            ON CONFLICT(week, day, room, screening, movie) DO NOTHING""",
            (self.week, self.day, self.room, self.screening, self.movie),
        )


class Query:
    def __init__(self, q):
        self.movie_filter = q["movie_filter"]
        self.characteristics = q["characteristics"]
        self.limit_function = q["limit_function"]
        self.time_grouping = q["time_grouping"]

    def parse_movie_filter(self):
        def parse(movie_filter):
            if not isinstance(movie_filter, list):
                return ""
            if len(movie_filter) == 0:
                return ""
            operation = movie_filter[0].lower()
            if operation == NOT:
                if len(movie_filter) != 2:
                    raise InvalidRule
                return "( NOT " + parse(movie_filter[1]) + ")"
            if len(movie_filter) != 3:
                raise InvalidRule
            if operation == OR:
                return (
                    "(" + parse(movie_filter[1]) + " OR " + parse(movie_filter[2]) + ")"
                )
            if operation == AND:
                return (
                    "("
                    + parse(movie_filter[1])
                    + " AND "
                    + parse(movie_filter[2])
                    + ")"
                )
            if operation == EQUAL:
                return "(" + movie_filter[1] + " = '" + movie_filter[2] + "')"
            raise InvalidRule

        return parse(self.movie_filter)

    def parse_characteristics(self):
        if not isinstance(self.characteristics, list):
            return set()
        if len(self.characteristics) == 0:
            return set()
        if self.characteristics[0] != "characteristics=":
            raise InvalidRule
        characteristics = set()
        for characteristic in self.characteristics[1:]:
            characteristics.add(characteristic)
        return characteristics

    def parse_limit_function(self):
        if not isinstance(self.limit_function, list):
            raise InvalidRule
        if len(self.limit_function) == 0:
            raise InvalidRule
        if self.limit_function[0] != "at_most" and self.limit_function[0] != "at_least":
            raise InvalidRule
        if len(self.limit_function) != 2:
            raise InvalidRule
        return (self.limit_function[0], self.limit_function[1])

    def parse_time_grouping(self):
        if not isinstance(self.time_grouping, list):
            raise InvalidRule
        if len(self.time_grouping) == 0:
            raise InvalidRule
        if self.time_grouping[0] != "every_n_days":
            raise InvalidRule
        if len(self.time_grouping) != 2:
            raise InvalidRule
        return self.time_grouping[1]
