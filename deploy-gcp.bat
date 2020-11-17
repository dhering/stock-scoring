@echo off
set CLOUDSDK_GSUTIL_PYTHON=%PYTHON37%python.exe

echo == sync gcp folder ==

call gsutil rsync -r gcp gs://stock-storage-sourcecode/gcp

echo == sync libs folder ==

call gsutil rsync -r -x ".*__pycache__.*" libs gs://stock-storage-sourcecode/libs

echo == deploy dumper cloud function

call gcloud functions deploy index-dumper-test --region europe-west3 --memory=128MB --runtime=python38 --source=dist/gcp-dumper-function.zip --max-instances=5 --trigger-topic=index-dump --entry-point=dump_index