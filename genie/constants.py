prompt_1 = f"""
Perform the following actions: \n
1 - Get clinical trials that contain word ```cancer``` case insensitive. \n
2 - From that take only those that have started between August 2016 and August 2021 including end of month. \n
3 - Count number of unique ids. \n
4 - Print only that number 
"""

prompt_2 = f"""
Perform the following actions: \n
1 - Get clinical trials that contain word ```cancer``` case insensitive. \n
2 - From that take only those that have started between August 2016 and August 2021 including end of month. \n
3 - From that take only those trials that involve drug interventions \n
4 - Count number of unique ids. \n
5 - Print only that number 
"""

prompt_3 = f"""
Perform the following actions: \n
1 - Get clinical trials that study```cancer``` condition, case insensitive. \n
2 - From that take only those that have started not earlier than last 5 years from 2023-05-21 including. \n
3 - From that take only those trials that involve drug interventions \n
4 - Per each unique status, return number of unique trial ids with that status \n
5 - Print result as a table with two columns ```status``` and ```n_studies``` \n
6 - Sort table by ```n_studies``` column descending.
"""
