Notes, Sources & Caveats

The members/add endpoint is not in the official dev docs, but community support threads describe it. It returns a results_id (HTTP 202) which you later poll via members/results. 
Google Groups

Poll creation is documented in the GroupMeCommunityDocs. 
GitHub

The official docs do not include all fields in responses; the community docs often fill in missing bits (e.g. poll messages). 
GitHub
+1

You may find subtle differences (data types, optional vs required) when testing in real API responses, so plan to adjust your spec accordingly.