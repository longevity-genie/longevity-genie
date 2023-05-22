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

prompt_4 = f"""
Perform the following actions: \n
1 - Get clinical trials that study```cancer``` condition, case insensitive. \n
2 - From that take only those that have started not earlier than last 5 years from 2023-05-21 including. \n
3 - From that take only those trials that involve drug interventions \n
4 - Create new column "is_successful" and fill it with boolean values. Column should have true values for successful trials and false for unsuccessful  \n
4 - Per each value of "is_successful" column, return number of unique trial ids with that status \n
5 - Print result as a table with two columns ```is_successful``` and ```n_studies``` \n
6 - Sort table by ```n_studies``` column descending.
"""

prompt_5 = f"""
Perform the following actions: \n
1 - Get clinical trials that study```cancer``` condition, case insensitive. \n
2 - From that take only those that have started not earlier than last 5 years from 2023-05-21 including. \n
3 - From that take only those trials that involve drug interventions \n
4 - Create new column "is_successful" and fill it with boolean values. Column should have true values for successful trials and false for unsuccessful  \n
5 - Take only rows where "is_successful" is False  \n
6 - Find id of the first trial in the dataset from the previous step \n
7 - Print id from the previous step \n
8 - Parse text of the response from this web page https://clinicaltrials.gov/ct2/show/```id```.\n
9 - Remove tags, styles and scripts, than remove new lines and get only text.\n
"""

prompt_6 = f"""
Perform the following actions: \n
1 - In the following text find detailed explanation of why trial was unsuccessful {0} \n
"""