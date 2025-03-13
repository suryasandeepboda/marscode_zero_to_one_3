Problem Statement:

I have a Google Sheet named “Marscode V2 responses”. Would like to extract specific columns like Context Awareness, Autonomy, Experience, Output Quality along with the ratings.
Requirements/Goals:
Access the Google Sheet “https://docs.google.com/spreadsheets/d/15FMeidgU2Dg7Q4JKPkLAdJmQ3IxWCWJXjhCo9UterCE/edit?gid=2052232470#gid=2052232470” using Google APIs with the Credentials.json
Extract specific columns like  Context Awareness, Autonomy, Experience, Output Quality along with the ratings.
Calculate the Mean Rating for all these metrics and introduce a new column in the output sheet named “Mean Rating”
Find the difference between Mean Rating and Overall Satisfaction column.
Introduce a new column called “Result” and mark this column “Ok” and color the cell green if the difference is in between -1 to 1.
Mark the “Result” column “Not ok” and color the cell “Red” if the difference is less than -1 and greater than +1.
The output columns should be “Email address”, “Tool used”, “Feature Used”, “Context Awareness”, “Autonomy”, “Experience”, “Output Quality”.”Overall Rating”, “Mean Rating”, “Difference”, “Result”, “Unique ID”, “Pod” and should be created in a Target Google sheet https://docs.google.com/spreadsheets/d/1FEqiDqqPfb9YHAWBiqVepmmXj22zNqXNNI7NLGCDVak/edit?gid=0#gid=0

Context/Tools:
Check that the Source Google sheet and Target Google sheet is shared with the Google Service Account for Read and Write access.
All the Python Google API dependencies are installed in the project
Task:
Please generate a concise, step-by-step plan or outline for addressing the above problem. The outline should include:
Overall Approach:
Summarize how you will structure the solution from start to finish.
Data/Resource Access:
Explain any required setup or authentication (if applicable).
Solution Steps:
List each major step to implement (e.g., retrieving data, processing/calculating values, handling edge cases, etc.).
Testing & Validation Strategy:
Briefly describe how you would test or verify each part of the solution.
Potential Edge Cases & Error Handling:
Indicate any likely pitfalls and how you’d handle them.
Format your response as a bullet-point or numbered outline. Avoid writing any actual code at this stage—focus on the plan itself.