## Description

**Info**: 
Run `app.py` with appropriate name of the 'Partner Finanicals' report (i.e. --task='headline') to create it and upload to s3 bucket. Bucket for test prupose is: `s3://etl-financials-claims-preprocess-{hsdk_env}/tmp`

## How to run:
1. Run jumpbox: `jumpbox 5439 hippo-redshift-cluster.co56vh5uqlw5.us-east-1.redshift.amazonaws.com 5439`
2. In new terminal window load env: `$(hsdk se d)` -> `2` 
3. Open /src folder and load ENV variables from local.sh: `source local.sh`
2. Run script depending on the task: `./app.py --task='headline'` or `./app.py --task='chain'` 
Data will be uploaded to local `/tmp` folder and s3 bucket: `s3://etl-financials-claims-preprocess-{hsdk_env}/tmp` 
