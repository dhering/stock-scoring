@echo off

echo == build dist ==
python gcp_dumper_build.py

echo == sync dist ==
call gsutil rsync -r dist gs://stock-storage-sourcecode/dist

echo == deploy dumper cloud function
call gcloud functions deploy index-dumper-test --region europe-west3 --memory=256MB --runtime=python38 --source=gs://stock-storage-sourcecode/dist/gcp-dumper-function.zip --max-instances=2 --trigger-topic=index-dump --entry-point=dump_index --set-env-vars LOG_LEVEL=INFO

call gcloud functions deploy stock-dumper --region europe-west3 --memory=256MB --runtime=python38 --source=gs://stock-storage-sourcecode/dist/gcp-dumper-function.zip --max-instances=10 --timeout=120 --trigger-topic=stock-dump --entry-point=dump_stock