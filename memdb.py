""" This module is responsible for handling the memory of the system."""

import sqlite3
import csv
import time
import movies as mvs


class MemDB:
    """This class is responsible for handling the memory of the system."""

    def __init__(self, db_name="movies.db"):
        self.conn = sqlite3.connect(db_name)
        cursor = self.conn.cursor()
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS movies 
            (title TEXT, year TEXT, genre TEXT, duration TEXT, 
            country TEXT, director TEXT, humor TEXT, rhythm TEXT, effort TEXT, 
            tension TEXT, vote TEXT, votes_total TEXT)"""
        )
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS past_screenings 
            (week INT, day INT, room INT, screening INT, movie TEXT)"""
        )
        # create unique index title
        cursor.execute(
            """CREATE UNIQUE INDEX IF NOT 
            EXISTS unique_idx_title_movies ON movies (title)"""
        )
        cursor.execute(
            """CREATE INDEX IF NOT EXISTS idx_title_past_screenings ON past_screenings (movie)"""
        )
        # this is just to make sure when server reinialized, we do not create
        # duplicate rows since there is no primary key
        cursor.execute(
            """CREATE UNIQUE INDEX IF NOT EXISTS 
            unique_idx_week_day_room_screening_movie_past_screenings 
            ON past_screenings (week, day, room, screening, movie)"""
        )
        self.conn.commit()
        cursor.close()

    def load_movies(self, filename):
        f = open(filename, "r")
        csvreader = csv.reader(f)
        next(csvreader)
        cursor = self.conn.cursor()
        for row in csvreader:
            movie = mvs.Movie(row)
            movie.insert_to_db(cursor)
        self.conn.commit()
        cursor.close()
        f.close()

    def load_past_screenings(self, filename):
        f = open(filename, "r")
        csvreader = csv.reader(f)
        cursor = self.conn.cursor()
        next(csvreader)
        for row in csvreader:
            past_screening = mvs.PastScreening(row)
            past_screening.insert_to_db(cursor)
        self.conn.commit()
        cursor.close()
        f.close()

    def query(self, query: mvs.Query):
        start = time.time()
        movie_filter = query.parse_movie_filter()
        limit = query.parse_limit_function()
        frequency = query.parse_time_grouping()
        characteristics = query.parse_characteristics()
        cursor = self.conn.cursor()

        # filter movies
        query_str = "SELECT * FROM movies WHERE " + movie_filter
        if len(movie_filter) == 0:
            query_str = "SELECT * FROM movies"
        movies = {}
        db_movies = cursor.execute(query_str).fetchall()
        for row in db_movies:
            movie = mvs.Movie(row)
            movies[movie.title] = movie
        movie_screenings = {}

        # get the past screenings for the movies
        weekly_screenings = {}
        for movie in movies.values():
            db_screenings = cursor.execute(
                "SELECT * FROM past_screenings WHERE movie = ?", (movie.title,)
            ).fetchall()
            screenings = [None] * len(db_screenings)
            for i, _ in enumerate(db_screenings):
                screenings[i] = mvs.PastScreening(db_screenings[i])
                if screenings[i].week not in weekly_screenings:
                    weekly_screenings[screenings[i].week] = []
                weekly_screenings[screenings[i].week].append(
                    (movie.title, screenings[i].day)
                )
            movie_screenings[movie.title] = screenings
        cursor.close()
        valid_weeks = 0

        # count the valid weeks
        for title_and_days in weekly_screenings.values():
            grouped_movies = self.group_by_characteristics(
                title_and_days, movies, characteristics
            )
            is_valid_week = limit[0] == mvs.AT_MOST
            for grouped_movie in grouped_movies.values():
                grouped_movie.sort()
                i = 0
                j = 0
                cnt = 0
                while j < len(grouped_movie):
                    if grouped_movie[j] - grouped_movie[i] <= frequency - 1:
                        cnt += 1
                        j += 1
                    else:
                        i += 1
                        cnt -= 1
                        continue
                    if limit[0] == mvs.AT_LEAST and cnt >= limit[1]:
                        is_valid_week = True
                        break
                    if limit[0] == mvs.AT_MOST and cnt > limit[1]:
                        is_valid_week = False
                        break
                if not is_valid_week:
                    break
            if is_valid_week:
                valid_weeks += 1
        print("Query took", round(time.time() - start, 2), "seconds")
        return valid_weeks

    def group_by_characteristics(
            self,
            title_and_days,
            movies,
            characteristics):
        group = {}
        for title_and_day in title_and_days:
            title, day = title_and_day[0], title_and_day[1]
            key = ""
            movie = movies[title]
            for characterisctic in characteristics:
                key += str(movie[characterisctic]) + "|"
            if key not in group:
                group[key] = []
            group[key].append(day)
        return group
