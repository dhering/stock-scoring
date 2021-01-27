@echo off

set BUCKET_SOURCECODE=gs://stock-storage-sourcecode

echo == check or create sourcecode bucket ==
call gsutil ls -b %BUCKET_SOURCECODE% || gsutil mb -l EUROPE-WEST3 %BUCKET_SOURCECODE%

echo == build dist ==
python gcp_dumper_build.py

echo == sync dist ==
call gsutil rsync -r dist %BUCKET_SOURCECODE%/dist

echo == deploy dumper cloud function
call gcloud functions deploy index-dumper --region europe-west3 --memory=256MB --runtime=python38 --source=%BUCKET_SOURCECODE%/dist/gcp-dumper-function.zip --max-instances=2 --trigger-topic=index-dump --entry-point=dump_index --set-env-vars LOG_LEVEL=INFO

call gcloud functions deploy stock-dumper --region europe-west3 --memory=256MB --runtime=python38 --source=%BUCKET_SOURCECODE%/dist/gcp-dumper-function.zip --max-instances=10 --timeout=120 --trigger-topic=stock-dump --entry-point=dump_stock