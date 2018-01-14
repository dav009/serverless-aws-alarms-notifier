cp serverless.yml tmp_serverless.yml
cp dummy.yml serverless.yml
sls plugin install -n serverless-python-requirements
cp tmp_serverless.yml serverless.yml
