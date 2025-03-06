 #!/bin/bash
curl -X POST http://127.0.0.1:5000/generate-chart \
-H "Content-Type: application/json" \
-d '{
      "file_path": "submissions.json"
    }'

curl -X POST http://127.0.0.1:5000/generate-chart \
-H "Content-Type: application/json" \
-d '{
      "file_path": "submissions.json",
      "filters": {
        "formName": "Sample Form",
        "state": "submitted"
      }
    }'

curl -X POST http://127.0.0.1:5000/query \
   -H "Content-Type: application/json" \
   -d '{
         "query": "Find all records with name Alice",
         "file_path": "random_ethnic_names_english.json",
         "start_date": "2023-01-01",
         "end_date": "2023-12-31",
         "fetch_all": true
       }'

curl -X POST http://127.0.0.1:5000/query \
          -H "Content-Type: application/json" \
          -d '{
                "query": "Find all records with name Alice",
                "file_path": "random_ethnic_names_english.json",
                "start_date": "2022-01-01",
                "end_date": "2022-12-31",
                "fetch_all": true
              }'

curl -X POST http://127.0.0.1:5000/query \
                 -H "Content-Type: application/json" \
                 -d '{
                       "query": "Find all records with name Alice",
                       "file_path": "random_ethnic_names_english.json",
                       "fetch_all": true
                     }'