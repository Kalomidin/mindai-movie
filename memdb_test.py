"""This module contains the tests for the memdb module."""

import unittest
import memdb
import movies

RAISE_EXCEPTION = "query() raised an exception"


def init():
    movies_filename = "data/movies.csv"
    past_screenings_filename = "data/past_screenings_test.csv"
    mem = memdb.MemDB("movies_test.db")
    mem.load_movies(movies_filename)
    mem.load_past_screenings(past_screenings_filename)
    return mem


class TestMemDB(unittest.TestCase):
    def test_query_by_genre(self):
        mem = init()
        # only one movie with genre Thriller and it is 2 times in 0 week 0 day
        rule = movies.Query(
            {
                "movie_filter": ["=", "genre", "Thriller"],
                "characteristics": ["characteristics=", "genre"],
                "limit_function": ["at_least", 2],
                "time_grouping": ["every_n_days", 5],
            }
        )
        try:
            res = mem.query(rule)
            self.assertEqual(res, 1)
        except Exception as e:
            self.fail(RAISE_EXCEPTION, e)

    def test_query_by_country(self):
        mem = init()
        rule = movies.Query(
            {
                "movie_filter": [
                    "AND",
                    ["=", "country", "Sweden"],
                    ["=", "genre", "Thriller"],
                ],
                "characteristics": ["characteristics=", "genre"],
                "limit_function": ["at_least", 2],
                "time_grouping": ["every_n_days", 5],
            }
        )
        try:
            res = mem.query(rule)
            self.assertEqual(res, 1)
        except Exception as e:
            self.fail(RAISE_EXCEPTION, e)

    def test_query_by_vote(self):
        mem = init()
        rule = movies.Query(
            {
                "movie_filter": [
                    "AND",
                    ["OR", ["=", "vote", "4"], ["=", "vote", "7"]],
                    ["OR", ["=", "genre", "Thriller"], ["=", "genre", "Drama"]],
                ],
                "characteristics": ["characteristics=", "vote"],
                "limit_function": ["at_most", 1],
                "time_grouping": ["every_n_days", 5],
            }
        )
        try:
            res = mem.query(rule)
            self.assertEqual(res, 1)
        except Exception as e:
            self.fail(RAISE_EXCEPTION, e)


# This block will allow the test to be run directly from the command line
if __name__ == "__main__":
    unittest.main()
