# Mind AI Movie Coding Test

## Introduction

This repository contains the implementation of the requirements outlined in `data/Cinema Screening Validation Challenge.pdf`.

## Design Choice

SQLite was chosen as the database due to its efficiency in storing data in memory and its support for SQL queries.
In the initial step, `movies` and `past_screenings_test` are loaded into two separate tables with their respective names. The following indices are also created:

1. An index on the `movie` column in the `past_screenings` table.
2. A unique index on the `title` column of the `movies` table to prevent duplicates during loading.
3. A unique index on the `(week, day, room, screening, movie)` columns of the `past_screenings` table to prevent duplicates during loading.

Upon receiving a query, the following algorithm is applied:

1. Select movies that match the `movie_filter`. These are referred to as `movies`.

2. Select `past_screenings` for the `movies`.

3. Using `past_screenings`, a dictionary `weekly_screenings` is created to map all movie screenings for the given week. The key is the week number, and the value is `(movie_title, day)`.

4. Iterate over `weekly_screenings`. For each week, group movies based on the selected characteristics. This is referred to as `grouped_movies`.
5. For each `grouped_movies`, apply the limit and frequency. If they satisfy the conditions, it is a valid week. Otherwise, it is an invalid week.
    - To further explain the process of applying the limit and frequency, the following steps are executed:
     - Initially, all existing screenings for the movie are sorted in ascending order.
     - A boolean variable `is_valid_week` is initialized to `True` if the `limit` is set to `at_most`, otherwise it is set to `False`.
     - The two-pointer algorithm is employed. The pointers `i` and `j`, along with a counter `cnt`, are initialized to zero.
     - The algorithm iterates over the sorted screenings.
     - For each screening, if the difference in days between the screenings at indices `i` and `j` is less than or equal to the specified `frequency`, the counter `cnt` is incremented. Otherwise, the pointer `i` is incremented and `cnt` is decremented(meaning it hit the maximum range that starts at `i`).
     - If the `limit` is set to `at_most` and the counter `cnt` exceeds the `limit_amount`, `is_valid_week` is set to `False`.
     - Conversely, if the `limit` is set to `at_least` and the counter `cnt` is equal to or greater than the `limit_amount`, `is_valid_week` is set to `True`.

## Testing

`past_screenings_test.csv` was created for testing purposes. Several tests were added to verify the validity of `limit` and `frequency`.
Tests were also added to verify that different `characteristics` work as expected and that the system supports different `movie_filter`.
