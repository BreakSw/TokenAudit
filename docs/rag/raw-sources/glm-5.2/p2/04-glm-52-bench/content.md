---
model: "GLM-5.2"
priority: "P2"
source_id: "04-glm-52-bench"
title: "AletheiaResearch/GLM-5.2-Bench · Datasets at Hugging Face"
source_url: "https://huggingface.co/datasets/AletheiaResearch/GLM-5.2-Bench"
final_url: "https://huggingface.co/datasets/AletheiaResearch/GLM-5.2-Bench"
captured_at: "2026-08-24T14:15:24.932Z"
capture_provider: "firecrawl"
accepted_for_review: true
sha256: "45bca7f6e5efd38cac3ac83008190ddcb09ffe3925fe623db46ee8d8ce2e4f29"
---
Dataset Preview

APIEmbed [Duplicate](https://huggingface.co/datasets/AletheiaResearch/GLM-5.2-Bench?duplicate=true)Data Studio

Subset (1)
default
default
Split (2)

passed
passedfailed

The full dataset viewer is not available (click to read why). Only showing a preview of the rows.

The dataset generation failed

```
Error code:   DatasetGenerationError
Exception:    FileNotFoundError
Message:      datasets/AletheiaResearch/GLM-5.2-Bench@fed533c5d959fb9f4295f661ea68e512f08a9fb5/passed/bench-terminal-bench-2.0-bn-fit-modify.jsonl (repository not found)
Traceback:    Traceback (most recent call last):
                File "/usr/local/lib/python3.14/site-packages/huggingface_hub/utils/_http.py", line 761, in hf_raise_for_status
                  response.raise_for_status()
                  ~~~~~~~~~~~~~~~~~~~~~~~~~^^
                File "/usr/local/lib/python3.14/site-packages/httpx/_models.py", line 829, in raise_for_status
                  raise HTTPStatusError(message, request=request, response=self)
              httpx.HTTPStatusError: Client error '401 Unauthorized' for url 'https://huggingface.co/api/datasets/AletheiaResearch/GLM-5.2-Bench/revision/fed533c5d959fb9f4295f661ea68e512f08a9fb5'
              For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/401

              The above exception was the direct cause of the following exception:

              Traceback (most recent call last):
                File "/usr/local/lib/python3.14/site-packages/huggingface_hub/hf_file_system.py", line 252, in _repo_and_revision_exist
                  self._api.repo_info(
                  ~~~~~~~~~~~~~~~~~~~^
                      repo_id, revision=revision, repo_type=repo_type, timeout=constants.HF_HUB_ETAG_TIMEOUT
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                  )
                  ^
                File "/usr/local/lib/python3.14/site-packages/huggingface_hub/utils/_validators.py", line 88, in _inner_fn
                  return fn(*args, **kwargs)
                File "/usr/local/lib/python3.14/site-packages/huggingface_hub/hf_api.py", line 3598, in repo_info
                  return method(
                      repo_id,
                  ...<4 lines>...
                      files_metadata=files_metadata,
                  )
                File "/usr/local/lib/python3.14/site-packages/huggingface_hub/utils/_validators.py", line 88, in _inner_fn
                  return fn(*args, **kwargs)
                File "/usr/local/lib/python3.14/site-packages/huggingface_hub/hf_api.py", line 3360, in dataset_info
                  hf_raise_for_status(r)
                  ~~~~~~~~~~~~~~~~~~~^^^
                File "/usr/local/lib/python3.14/site-packages/huggingface_hub/utils/_http.py", line 835, in hf_raise_for_status
                  raise _format(RepositoryNotFoundError, message, response, repo_type=repo_type, repo_id=repo_id) from e
              huggingface_hub.errors.RepositoryNotFoundError: 401 Client Error. (Request ID: Root=1-6a3c217d-207e79775ff988790cab0d54;8391652f-caa9-4aac-bd2d-f0a2bf3b0ccb)

              Repository Not Found for url: https://huggingface.co/api/datasets/AletheiaResearch/GLM-5.2-Bench/revision/fed533c5d959fb9f4295f661ea68e512f08a9fb5.
              Please make sure you specified the correct `repo_id` and `repo_type`.
              If you are trying to access a private or gated repo, make sure you are authenticated and your token has the required permissions.
              For more details, see https://huggingface.co/docs/huggingface_hub/authentication
              Invalid username or password.

              The above exception was the direct cause of the following exception:

              Traceback (most recent call last):
                File "/usr/local/lib/python3.14/site-packages/datasets/builder.py", line 1816, in _prepare_split_single
                  for key, table in generator:
                                    ^^^^^^^^^
                File "/src/services/worker/src/worker/job_runners/config/parquet_and_info.py", line 613, in wrapped
                  for item in generator(*args, **kwargs):
                              ~~~~~~~~~^^^^^^^^^^^^^^^^^
                File "/usr/local/lib/python3.14/site-packages/datasets/packaged_modules/json/json.py", line 174, in _generate_tables
                  trace = trace_file.read_text(encoding="utf-8")
                File "/usr/local/lib/python3.14/pathlib/__init__.py", line 787, in read_text
                  with self.open(mode='r', encoding=encoding, errors=errors, newline=newline) as f:
                       ~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                File "/usr/local/lib/python3.14/site-packages/datasets/utils/file_utils.py", line 1223, in open
                  return xopen(str(self), *args, **kwargs)
                File "/usr/local/lib/python3.14/site-packages/datasets/utils/file_utils.py", line 982, in xopen
                  file_obj = fs.open(paths[0], mode)
                File "<string>", line 3, in open
                File "/usr/local/lib/python3.14/unittest/mock.py", line 1176, in __call__
                  return self._mock_call(*args, **kwargs)
                         ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^
                File "/usr/local/lib/python3.14/unittest/mock.py", line 1180, in _mock_call
                  return self._execute_mock_call(*args, **kwargs)
                         ~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^
                File "/usr/local/lib/python3.14/unittest/mock.py", line 1247, in _execute_mock_call
                  result = effect(*args, **kwargs)
                File "/src/services/worker/src/worker/job_runners/config/parquet_and_info.py", line 774, in wrapped
                  f = fs_open(self, urlpath, mode, *args, **kwargs)
                File "/usr/local/lib/python3.14/site-packages/fsspec/spec.py", line 1281, in open
                  self.open(
                  ~~~~~~~~~^
                      path,
                      ^^^^^
                  ...<4 lines>...
                      **kwargs,
                      ^^^^^^^^^
                  ),
                  ^
                File "<string>", line 3, in open
                File "/usr/local/lib/python3.14/unittest/mock.py", line 1176, in __call__
                  return self._mock_call(*args, **kwargs)
                         ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^
                File "/usr/local/lib/python3.14/unittest/mock.py", line 1180, in _mock_call
                  return self._execute_mock_call(*args, **kwargs)
                         ~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^
                File "/usr/local/lib/python3.14/unittest/mock.py", line 1247, in _execute_mock_call
                  result = effect(*args, **kwargs)
                File "/src/services/worker/src/worker/job_runners/config/parquet_and_info.py", line 774, in wrapped
                  f = fs_open(self, urlpath, mode, *args, **kwargs)
                File "/usr/local/lib/python3.14/site-packages/fsspec/spec.py", line 1293, in open
                  f = self._open(
                      path,
                  ...<4 lines>...
                      **kwargs,
                  )
                File "/usr/local/lib/python3.14/site-packages/huggingface_hub/hf_file_system.py", line 404, in _open
                  return HfFileSystemFile(self, path, mode=mode, revision=revision, **kwargs)
                File "/usr/local/lib/python3.14/site-packages/huggingface_hub/hf_file_system.py", line 1172, in __init__
                  self.resolved_path = fs.resolve_path(path, revision=revision)
                                       ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^
                File "/usr/local/lib/python3.14/site-packages/huggingface_hub/hf_file_system.py", line 341, in resolve_path
                  _raise_file_not_found(path, err)
                  ~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^
                File "/usr/local/lib/python3.14/site-packages/huggingface_hub/hf_file_system.py", line 1409, in _raise_file_not_found
                  raise FileNotFoundError(msg) from err
              FileNotFoundError: datasets/AletheiaResearch/GLM-5.2-Bench@fed533c5d959fb9f4295f661ea68e512f08a9fb5/passed/bench-terminal-bench-2.0-bn-fit-modify.jsonl (repository not found)

              The above exception was the direct cause of the following exception:

              Traceback (most recent call last):
                File "/src/services/worker/src/worker/job_runners/config/parquet_and_info.py", line 1369, in compute_config_parquet_and_info_response
                  parquet_operations, partial, estimated_dataset_info = stream_convert_to_parquet(
                                                                        ~~~~~~~~~~~~~~~~~~~~~~~~~^
                      builder, max_dataset_size_bytes=max_dataset_size_bytes
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                  )
                  ^
                File "/src/services/worker/src/worker/job_runners/config/parquet_and_info.py", line 948, in stream_convert_to_parquet
                  builder._prepare_split(split_generator=splits_generators[split], file_format="parquet")
                  ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                File "/usr/local/lib/python3.14/site-packages/datasets/builder.py", line 1683, in _prepare_split
                  for job_id, done, content in self._prepare_split_single(
                                               ~~~~~~~~~~~~~~~~~~~~~~~~~~^
                      gen_kwargs=gen_kwargs, job_id=job_id, **_prepare_split_args
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                  ):
                  ^
                File "/usr/local/lib/python3.14/site-packages/datasets/builder.py", line 1869, in _prepare_split_single
                  raise DatasetGenerationError("An error occurred while generating the dataset") from e
              datasets.exceptions.DatasetGenerationError: An error occurred while generating the dataset
```

Need help to make the dataset viewer work? Make sure to review [how to configure the dataset viewer](https://huggingface.co/docs/hub/datasets-data-files-configuration), and [open a discussion](https://huggingface.co/datasets/AletheiaResearch/GLM-5.2-Bench/discussions/new?title=Dataset+Viewer+issue%3A+DatasetGenerationError&description=The+dataset+viewer+is+not+working.%0A%0AError+details%3A%0A%0A%60%60%60%0AError+code%3A+++DatasetGenerationError%0AException%3A++++FileNotFoundError%0AMessage%3A++++++datasets%2FAletheiaResearch%2FGLM-5.2-Bench%40fed533c5d959fb9f4295f661ea68e512f08a9fb5%2Fpassed%2Fbench-terminal-bench-2.0-bn-fit-modify.jsonl+%28repository+not+found%29%0ATraceback%3A++++Traceback+%28most+recent+call+last%29%3A%0A++++++++++++++++File+%22%2Fusr%2Flocal%2Flib%2Fpython3.14%2Fsite-packages%2Fhuggingface_hub%2Futils%2F_http.py%22%2C+line+761%2C+in+hf_raise_for_status%0A++++++++++++++++++response.raise_for_status%28%29%0A++++++++++++++++++%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%5E%5E%0A++++++++++++++++File+%22%2Fusr%2Flocal%2Flib%2Fpython3.14%2Fsite-packages%2Fhttpx%2F_models.py%22%2C+line+829%2C+in+raise_for_status%0A++++++++++++++++++raise+HTTPStatusError%28message%2C+request%3Drequest%2C+response%3Dself%29%0A++++++++++++++httpx.HTTPStatusError%3A+Client+error+%27401+Unauthorized%27+for+url+%27https%3A%2F%2Fhuggingface.co%2Fapi%2Fdatasets%2FAletheiaResearch%2FGLM-5.2-Bench%2Frevision%2Ffed533c5d959fb9f4295f661ea68e512f08a9fb5%27%0A++++++++++++++For+more+information+check%3A+https%3A%2F%2Fdeveloper.mozilla.org%2Fen-US%2Fdocs%2FWeb%2FHTTP%2FStatus%2F401%0A++++++++++++++%0A++++++++++++++The+above+exception+was+the+direct+cause+of+the+following+exception%3A%0A++++++++++++++%0A++++++++++++++Traceback+%28most+recent+call+last%29%3A%0A++++++++++++++++File+%22%2Fusr%2Flocal%2Flib%2Fpython3.14%2Fsite-packages%2Fhuggingface_hub%2Fhf_file_system.py%22%2C+line+252%2C+in+_repo_and_revision_exist%0A++++++++++++++++++self._api.repo_info%28%0A++++++++++++++++++%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%5E%0A++++++++++++++++++++++repo_id%2C+revision%3Drevision%2C+repo_type%3Drepo_type%2C+timeout%3Dconstants.HF_HUB_ETAG_TIMEOUT%0A++++++++++++++++++++++%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%0A++++++++++++++++++%29%0A++++++++++++++++++%5E%0A++++++++++++++++File+%22%2Fusr%2Flocal%2Flib%2Fpython3.14%2Fsite-packages%2Fhuggingface_hub%2Futils%2F_validators.py%22%2C+line+88%2C+in+_inner_fn%0A++++++++++++++++++return+fn%28*args%2C+**kwargs%29%0A++++++++++++++++File+%22%2Fusr%2Flocal%2Flib%2Fpython3.14%2Fsite-packages%2Fhuggingface_hub%2Fhf_api.py%22%2C+line+3598%2C+in+repo_info%0A++++++++++++++++++return+method%28%0A++++++++++++++++++++++repo_id%2C%0A++++++++++++++++++...%3C4+lines%3E...%0A++++++++++++++++++++++files_metadata%3Dfiles_metadata%2C%0A++++++++++++++++++%29%0A++++++++++++++++File+%22%2Fusr%2Flocal%2Flib%2Fpython3.14%2Fsite-packages%2Fhuggingface_hub%2Futils%2F_validators.py%22%2C+line+88%2C+in+_inner_fn%0A++++++++++++++++++return+fn%28*args%2C+**kwargs%29%0A++++++++++++++++File+%22%2Fusr%2Flocal%2Flib%2Fpython3.14%2Fsite-packages%2Fhuggingface_hub%2Fhf_api.py%22%2C+line+3360%2C+in+dataset_info%0A++++++++++++++++++hf_raise_for_status%28r%29%0A++++++++++++++++++%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%5E%5E%5E%0A++++++++++++++++File+%22%2Fusr%2Flocal%2Flib%2Fpython3.14%2Fsite-packages%2Fhuggingface_hub%2Futils%2F_http.py%22%2C+line+835%2C+in+hf_raise_for_status%0A++++++++++++++++++raise+_format%28RepositoryNotFoundError%2C+message%2C+response%2C+repo_type%3Drepo_type%2C+repo_id%3Drepo_id%29+from+e%0A++++++++++++++huggingface_hub.errors.RepositoryNotFoundError%3A+401+Client+Error.+%28Request+ID%3A+Root%3D1-6a3c217d-207e79775ff988790cab0d54%3B8391652f-caa9-4aac-bd2d-f0a2bf3b0ccb%29%0A++++++++++++++%0A++++++++++++++Repository+Not+Found+for+url%3A+https%3A%2F%2Fhuggingface.co%2Fapi%2Fdatasets%2FAletheiaResearch%2FGLM-5.2-Bench%2Frevision%2Ffed533c5d959fb9f4295f661ea68e512f08a9fb5.%0A++++++++++++++Please+make+sure+you+specified+the+correct+%60repo_id%60+and+%60repo_type%60.%0A++++++++++++++If+you+are+trying+to+access+a+private+or+gated+repo%2C+make+sure+you+are+authenticated+and+your+token+has+the+required+permissions.%0A++++++++++++++For+more+details%2C+see+https%3A%2F%2Fhuggingface.co%2Fdocs%2Fhuggingface_hub%2Fauthentication%0A++++++++++++++Invalid+username+or+password.%0A++++++++++++++%0A++++++++++++++The+above+exception+was+the+direct+cause+of+the+following+exception%3A%0A++++++++++++++%0A++++++++++++++Traceback+%28most+recent+call+last%29%3A%0A++++++++++++++++File+%22%2Fusr%2Flocal%2Flib%2Fpython3.14%2Fsite-packages%2Fdatasets%2Fbuilder.py%22%2C+line+1816%2C+in+_prepare_split_single%0A++++++++++++++++++for+key%2C+table+in+generator%3A%0A++++++++++++++++++++++++++++++++++++%5E%5E%5E%5E%5E%5E%5E%5E%5E%0A++++++++++++++++File+%22%2Fsrc%2Fservices%2Fworker%2Fsrc%2Fworker%2Fjob_runners%2Fconfig%2Fparquet_and_info.py%22%2C+line+613%2C+in+wrapped%0A++++++++++++++++++for+item+in+generator%28*args%2C+**kwargs%29%3A%0A++++++++++++++++++++++++++++++%7E%7E%7E%7E%7E%7E%7E%7E%7E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%0A++++++++++++++++File+%22%2Fusr%2Flocal%2Flib%2Fpython3.14%2Fsite-packages%2Fdatasets%2Fpackaged_modules%2Fjson%2Fjson.py%22%2C+line+174%2C+in+_generate_tables%0A++++++++++++++++++trace+%3D+trace_file.read_text%28encoding%3D%22utf-8%22%29%0A++++++++++++++++File+%22%2Fusr%2Flocal%2Flib%2Fpython3.14%2Fpathlib%2F__init__.py%22%2C+line+787%2C+in+read_text%0A++++++++++++++++++with+self.open%28mode%3D%27r%27%2C+encoding%3Dencoding%2C+errors%3Derrors%2C+newline%3Dnewline%29+as+f%3A%0A+++++++++++++++++++++++%7E%7E%7E%7E%7E%7E%7E%7E%7E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%0A++++++++++++++++File+%22%2Fusr%2Flocal%2Flib%2Fpython3.14%2Fsite-packages%2Fdatasets%2Futils%2Ffile_utils.py%22%2C+line+1223%2C+in+open%0A++++++++++++++++++return+xopen%28str%28self%29%2C+*args%2C+**kwargs%29%0A++++++++++++++++File+%22%2Fusr%2Flocal%2Flib%2Fpython3.14%2Fsite-packages%2Fdatasets%2Futils%2Ffile_utils.py%22%2C+line+982%2C+in+xopen%0A++++++++++++++++++file_obj+%3D+fs.open%28paths%5B0%5D%2C+mode%29%0A++++++++++++++++File+%22%3Cstring%3E%22%2C+line+3%2C+in+open%0A++++++++++++++++File+%22%2Fusr%2Flocal%2Flib%2Fpython3.14%2Funittest%2Fmock.py%22%2C+line+1176%2C+in+__call__%0A++++++++++++++++++return+self._mock_call%28*args%2C+**kwargs%29%0A+++++++++++++++++++++++++%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%0A++++++++++++++++File+%22%2Fusr%2Flocal%2Flib%2Fpython3.14%2Funittest%2Fmock.py%22%2C+line+1180%2C+in+_mock_call%0A++++++++++++++++++return+self._execute_mock_call%28*args%2C+**kwargs%29%0A+++++++++++++++++++++++++%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%0A++++++++++++++++File+%22%2Fusr%2Flocal%2Flib%2Fpython3.14%2Funittest%2Fmock.py%22%2C+line+1247%2C+in+_execute_mock_call%0A++++++++++++++++++result+%3D+effect%28*args%2C+**kwargs%29%0A++++++++++++++++File+%22%2Fsrc%2Fservices%2Fworker%2Fsrc%2Fworker%2Fjob_runners%2Fconfig%2Fparquet_and_info.py%22%2C+line+774%2C+in+wrapped%0A++++++++++++++++++f+%3D+fs_open%28self%2C+urlpath%2C+mode%2C+*args%2C+**kwargs%29%0A++++++++++++++++File+%22%2Fusr%2Flocal%2Flib%2Fpython3.14%2Fsite-packages%2Ffsspec%2Fspec.py%22%2C+line+1281%2C+in+open%0A++++++++++++++++++self.open%28%0A++++++++++++++++++%7E%7E%7E%7E%7E%7E%7E%7E%7E%5E%0A++++++++++++++++++++++path%2C%0A++++++++++++++++++++++%5E%5E%5E%5E%5E%0A++++++++++++++++++...%3C4+lines%3E...%0A++++++++++++++++++++++**kwargs%2C%0A++++++++++++++++++++++%5E%5E%5E%5E%5E%5E%5E%5E%5E%0A++++++++++++++++++%29%2C%0A++++++++++++++++++%5E%0A++++++++++++++++File+%22%3Cstring%3E%22%2C+line+3%2C+in+open%0A++++++++++++++++File+%22%2Fusr%2Flocal%2Flib%2Fpython3.14%2Funittest%2Fmock.py%22%2C+line+1176%2C+in+__call__%0A++++++++++++++++++return+self._mock_call%28*args%2C+**kwargs%29%0A+++++++++++++++++++++++++%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%0A++++++++++++++++File+%22%2Fusr%2Flocal%2Flib%2Fpython3.14%2Funittest%2Fmock.py%22%2C+line+1180%2C+in+_mock_call%0A++++++++++++++++++return+self._execute_mock_call%28*args%2C+**kwargs%29%0A+++++++++++++++++++++++++%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%0A++++++++++++++++File+%22%2Fusr%2Flocal%2Flib%2Fpython3.14%2Funittest%2Fmock.py%22%2C+line+1247%2C+in+_execute_mock_call%0A++++++++++++++++++result+%3D+effect%28*args%2C+**kwargs%29%0A++++++++++++++++File+%22%2Fsrc%2Fservices%2Fworker%2Fsrc%2Fworker%2Fjob_runners%2Fconfig%2Fparquet_and_info.py%22%2C+line+774%2C+in+wrapped%0A++++++++++++++++++f+%3D+fs_open%28self%2C+urlpath%2C+mode%2C+*args%2C+**kwargs%29%0A++++++++++++++++File+%22%2Fusr%2Flocal%2Flib%2Fpython3.14%2Fsite-packages%2Ffsspec%2Fspec.py%22%2C+line+1293%2C+in+open%0A++++++++++++++++++f+%3D+self._open%28%0A++++++++++++++++++++++path%2C%0A++++++++++++++++++...%3C4+lines%3E...%0A++++++++++++++++++++++**kwargs%2C%0A++++++++++++++++++%29%0A++++++++++++++++File+%22%2Fusr%2Flocal%2Flib%2Fpython3.14%2Fsite-packages%2Fhuggingface_hub%2Fhf_file_system.py%22%2C+line+404%2C+in+_open%0A++++++++++++++++++return+HfFileSystemFile%28self%2C+path%2C+mode%3Dmode%2C+revision%3Drevision%2C+**kwargs%29%0A++++++++++++++++File+%22%2Fusr%2Flocal%2Flib%2Fpython3.14%2Fsite-packages%2Fhuggingface_hub%2Fhf_file_system.py%22%2C+line+1172%2C+in+__init__%0A++++++++++++++++++self.resolved_path+%3D+fs.resolve_path%28path%2C+revision%3Drevision%29%0A+++++++++++++++++++++++++++++++++++++++%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%0A++++++++++++++++File+%22%2Fusr%2Flocal%2Flib%2Fpython3.14%2Fsite-packages%2Fhuggingface_hub%2Fhf_file_system.py%22%2C+line+341%2C+in+resolve_path%0A++++++++++++++++++_raise_file_not_found%28path%2C+err%29%0A++++++++++++++++++%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%0A++++++++++++++++File+%22%2Fusr%2Flocal%2Flib%2Fpython3.14%2Fsite-packages%2Fhuggingface_hub%2Fhf_file_system.py%22%2C+line+1409%2C+in+_raise_file_not_found%0A++++++++++++++++++raise+FileNotFoundError%28msg%29+from+err%0A++++++++++++++FileNotFoundError%3A+datasets%2FAletheiaResearch%2FGLM-5.2-Bench%40fed533c5d959fb9f4295f661ea68e512f08a9fb5%2Fpassed%2Fbench-terminal-bench-2.0-bn-fit-modify.jsonl+%28repository+not+found%29%0A++++++++++++++%0A++++++++++++++The+above+exception+was+the+direct+cause+of+the+following+exception%3A%0A++++++++++++++%0A++++++++++++++Traceback+%28most+recent+call+last%29%3A%0A++++++++++++++++File+%22%2Fsrc%2Fservices%2Fworker%2Fsrc%2Fworker%2Fjob_runners%2Fconfig%2Fparquet_and_info.py%22%2C+line+1369%2C+in+compute_config_parquet_and_info_response%0A++++++++++++++++++parquet_operations%2C+partial%2C+estimated_dataset_info+%3D+stream_convert_to_parquet%28%0A++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%5E%0A++++++++++++++++++++++builder%2C+max_dataset_size_bytes%3Dmax_dataset_size_bytes%0A++++++++++++++++++++++%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%0A++++++++++++++++++%29%0A++++++++++++++++++%5E%0A++++++++++++++++File+%22%2Fsrc%2Fservices%2Fworker%2Fsrc%2Fworker%2Fjob_runners%2Fconfig%2Fparquet_and_info.py%22%2C+line+948%2C+in+stream_convert_to_parquet%0A++++++++++++++++++builder._prepare_split%28split_generator%3Dsplits_generators%5Bsplit%5D%2C+file_format%3D%22parquet%22%29%0A++++++++++++++++++%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%0A++++++++++++++++File+%22%2Fusr%2Flocal%2Flib%2Fpython3.14%2Fsite-packages%2Fdatasets%2Fbuilder.py%22%2C+line+1683%2C+in+_prepare_split%0A++++++++++++++++++for+job_id%2C+done%2C+content+in+self._prepare_split_single%28%0A+++++++++++++++++++++++++++++++++++++++++++++++%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%7E%5E%0A++++++++++++++++++++++gen_kwargs%3Dgen_kwargs%2C+job_id%3Djob_id%2C+**_prepare_split_args%0A++++++++++++++++++++++%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%5E%0A++++++++++++++++++%29%3A%0A++++++++++++++++++%5E%0A++++++++++++++++File+%22%2Fusr%2Flocal%2Flib%2Fpython3.14%2Fsite-packages%2Fdatasets%2Fbuilder.py%22%2C+line+1869%2C+in+_prepare_split_single%0A++++++++++++++++++raise+DatasetGenerationError%28%22An+error+occurred+while+generating+the+dataset%22%29+from+e%0A++++++++++++++datasets.exceptions.DatasetGenerationError%3A+An+error+occurred+while+generating+the+dataset%0A%60%60%60%0A%0A%0Acc+%40lhoestq+%40cfahlgren1.) for direct support.

| harness<br>string | session\_id<br>string | prompt<br>string | messages<br>list | tools<br>list | metadata<br>unknown | sent\_at<br>string | num\_user\_messages<br>int64 | num\_tool\_calls<br>int64 | trace<br>unknown | file\_path<br>string |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| pi | 019efa62-6861-769e-ac7d-ad09e83dac4c | You are provided with a dataset sample from a Bayesian Network in /app/bn\_sample\_10k.csv. <br>Your first task is to recover the underlying DAG using the provided data.<br>Here is some information about the original DAG that you may find useful:<br>\- U has no parents <br>\- There are six total edges in the DAG that the data was... | \[<br>{<br>"role": "user",<br>"content": "You are provided with a dataset sample from a Bayesian Network in /app/bn\_sample\_10k.csv. \\nYour first task is to recover the underlying DAG using the provided data.\\n\\nHere is some information about the original DAG that you may find useful:\\n - U has no parents \\n - There a... | \[<br>{<br>"type": "function",<br>"function": {<br>"name": "bash",<br>"parameters": {<br>"type": "object",<br>"properties": {<br>"command": {<br>"type": "string"<br>}<br>},<br>"additionalProperties": true,<br>"required": \[<br>"command"<br>\]<br>}<br>}... | {<br>"source\_file": "bench-terminal-bench-2.0-bn-fit-modify.jsonl",<br>"session\_id": "019efa62-6861-769e-ac7d-ad09e83dac4c",<br>"trace\_type": "pi",<br>"model\_provider": "openrouter",<br>"model": "z-ai/glm-5.2",<br>"cwd": "/app",<br>"cli\_version": null,<br>"turn\_count": 1,<br>"first\_message\_timestamp": "2026-06-24T16:06:53.83200... | null | 1 | 10 | "{\\"type\\": \\"session\\", \\"version\\": 3, \\"id\\": \\"019efa62-6861-769e-ac7d-ad09e83dac4c\\", \\"timestamp\\": \\"2026-06-24T16:06:53.795Z\\", \\"cwd\\": \\"/app\\"}\\n{\\"type\\": \\"message\\", \\"message\\": {\\"role\\": \\"user\\", \\"content\\": \[{\\"type\\": \\"text\\", \\"text\\": \\"You are provided with a dataset sample from a Bayesian Netw... | passed/bench-terminal-bench-2.0-bn-fit-modify.jsonl |\
| pi | 019efa62-675d-7328-9e7c-52a441ea555e | There's a /app/filter.py script that attempts to remove JavaScript from HTML files to prevent XSS attacks.<br>The /app/filter.py script takes an HTML file as a command-line argument and modifies it in-place.<br>Usage: python /app/filter.py <html\_file><br>Your task is to create a file called /app/out.html that, even after bein... | \[{"role":"user","content":"There's a /app/filter.py script that attempts to remove JavaScript from H(...TRUNCATED) | \[{"type":"function","function":{"name":"bash","parameters":{"type":"object","properties":{"command":(...TRUNCATED) | {"source\_file":"bench-terminal-bench-2.0-break-filter-js-from-html.jsonl","session\_id":"019efa62-675(...TRUNCATED) | null | 1 | 23 | [View Pi session](https://huggingface.co/datasets/AletheiaResearch/GLM-5.2-Bench/blob/main/passed/bench-terminal-bench-2.0-break-filter-js-from-html.jsonl "View Pi session")"{\\"type\\": \\"session\\", \\"version\\": 3, \\"id\\": \\"019efa62-675d-7328-9e7c-52a441ea555e\\", \\"timesta(...TRUNCATED) | passed/bench-terminal-bench-2.0-break-filter-js-from-html.jsonl |\
| pi | 019efa62-66d7-74dd-9fc1-a44896c88f6a | pyknotid is a Python package for computational topology and knot theory.<br>I want to use its fast Cython extensions implemented (chelpers, ccomplexity, cinvariants), but it is incompatible with my existing Numpy versions in my system's global Python environment.<br>Directly pip installing from Pypi will not be compatible wi... | \[{"role":"user","content":"pyknotid is a Python package for computational topology and knot theory.\(...TRUNCATED) | \[{"type":"function","function":{"name":"bash","parameters":{"type":"object","properties":{"command":(...TRUNCATED) | {"source\_file":"bench-terminal-bench-2.0-build-cython-ext.jsonl","session\_id":"019efa62-66d7-74dd-9f(...TRUNCATED) | null | 1 | 40 | [View Pi session](https://huggingface.co/datasets/AletheiaResearch/GLM-5.2-Bench/blob/main/passed/bench-terminal-bench-2.0-build-cython-ext.jsonl "View Pi session")"{\\"type\\": \\"session\\", \\"version\\": 3, \\"id\\": \\"019efa62-66d7-74dd-9fc1-a44896c88f6a\\", \\"timesta(...TRUNCATED) | passed/bench-terminal-bench-2.0-build-cython-ext.jsonl |\
| pi | 019efa65-83a3-742d-b974-ae1d2f9fa1ba | Build pMARS (http://www.koth.org/pmars/) from source with no X server. <br>Since koth.org is unreliable, get the source from Debian packages instead. Extract the source to \`/app\` and build without X11 support. Install the binary to \`/usr/local/bin/pmars\`.<br>You can test your build with this command: \`pmars -b -r 50 -f fla... | \[{"role":"user","content":"Build pMARS (http://www.koth.org/pmars/) from source with no X server. \\n(...TRUNCATED) | \[{"type":"function","function":{"name":"bash","parameters":{"type":"object","properties":{"command":(...TRUNCATED) | {"source\_file":"bench-terminal-bench-2.0-build-pmars.jsonl","session\_id":"019efa65-83a3-742d-b974-ae(...TRUNCATED) | null | 1 | 23 | [View Pi session](https://huggingface.co/datasets/AletheiaResearch/GLM-5.2-Bench/blob/main/passed/bench-terminal-bench-2.0-build-pmars.jsonl "View Pi session")"{\\"type\\": \\"session\\", \\"version\\": 3, \\"id\\": \\"019efa65-83a3-742d-b974-ae1d2f9fa1ba\\", \\"timesta(...TRUNCATED) | passed/bench-terminal-bench-2.0-build-pmars.jsonl |\
| pi | 019efa68-aac1-754b-acb7-230b86187fc8 | Build POV-Ray 2.2. Find and download the source archives, extract them to \`/app/povray-2.2\`, then compile and install to \`/usr/local/bin/povray\`.<br> <br>We will test your build by rendering \`/app/deps/illum1.pov\` and comparing against a reference image.<br>Do not modify \`/app/deps/illum1.pov\`.<br>As a sanity check to see if you... | \[{"role":"user","content":"Build POV-Ray 2.2. Find and download the source archives, extract them to(...TRUNCATED) | \[{"type":"function","function":{"name":"bash","parameters":{"type":"object","properties":{"command":(...TRUNCATED) | {"source\_file":"bench-terminal-bench-2.0-build-pov-ray.jsonl","session\_id":"019efa68-aac1-754b-acb7-(...TRUNCATED) | null | 1 | 47 | [View Pi session](https://huggingface.co/datasets/AletheiaResearch/GLM-5.2-Bench/blob/main/passed/bench-terminal-bench-2.0-build-pov-ray.jsonl "View Pi session")"{\\"type\\": \\"session\\", \\"version\\": 3, \\"id\\": \\"019efa68-aac1-754b-acb7-230b86187fc8\\", \\"timesta(...TRUNCATED) | passed/bench-terminal-bench-2.0-build-pov-ray.jsonl |\
| pi | 019efa6a-d0fd-758f-b00d-fe2958d0b52a | Create a Python function called \`async run\_tasks(tasks: list\[Callable\[\[\], Awaitable\[None\]\]\], max\_concurrent: int) -> None\` where each task is an async job to be run and \`max\_concurrent\` is the max number of tasks that can be run concurrently. Put the function in a file called \`/app/run.py\` so that it can be imported us... | \[{"role":"user","content":"Create a Python function called \`async run\_tasks(tasks: list\[Callable\[\[\],(...TRUNCATED) | \[{"type":"function","function":{"name":"bash","parameters":{"type":"object","properties":{"command":(...TRUNCATED) | {"source\_file":"bench-terminal-bench-2.0-cancel-async-tasks.jsonl","session\_id":"019efa6a-d0fd-758f-(...TRUNCATED) | null | 1 | 10 | [View Pi session](https://huggingface.co/datasets/AletheiaResearch/GLM-5.2-Bench/blob/main/passed/bench-terminal-bench-2.0-cancel-async-tasks.jsonl "View Pi session")"{\\"type\\": \\"session\\", \\"version\\": 3, \\"id\\": \\"019efa6a-d0fd-758f-b00d-fe2958d0b52a\\", \\"timesta(...TRUNCATED) | passed/bench-terminal-bench-2.0-cancel-async-tasks.jsonl |\
| pi | 019efa6f-2992-713b-9b73-45d77a42c3a2 | You are given a COBOL program located at /app/src/program.cbl. This program reads input data from /app/src/INPUT.DAT and modifies one or more .DAT files located in the /app/data/ directory. The COBOL program is designed to be run from the /app/ directory and should be compiled and executed using GnuCOBOL 3.<br>Your task i... | \[{"role":"user","content":"You are given a COBOL program located at /app/src/program.cbl. This progr(...TRUNCATED) | \[{"type":"function","function":{"name":"bash","parameters":{"type":"object","properties":{"command":(...TRUNCATED) | {"source\_file":"bench-terminal-bench-2.0-cobol-modernization.jsonl","session\_id":"019efa6f-2992-713b(...TRUNCATED) | null | 1 | 28 | [View Pi session](https://huggingface.co/datasets/AletheiaResearch/GLM-5.2-Bench/blob/main/passed/bench-terminal-bench-2.0-cobol-modernization.jsonl "View Pi session")"{\\"type\\": \\"session\\", \\"version\\": 3, \\"id\\": \\"019efa6f-2992-713b-9b73-45d77a42c3a2\\", \\"timesta(...TRUNCATED) | passed/bench-terminal-bench-2.0-cobol-modernization.jsonl |\
| pi | 019efa71-640d-7060-8cd3-7ea1bae9b803 | Under /tmp/CompCert/, build the CompCert C verified compiler (version 3.13.1) from source,<br>configuring it to the operating system and instruction set architecture of the development<br>environment. Ensure that CompCert can be invoked through /tmp/CompCert/ccomp. CompCert must<br>be freshly built from source and fully functio... | \[{"role":"user","content":"Under /tmp/CompCert/, build the CompCert C verified compiler (version 3.1(...TRUNCATED) | \[{"type":"function","function":{"name":"bash","parameters":{"type":"object","properties":{"command":(...TRUNCATED) | {"source\_file":"bench-terminal-bench-2.0-compile-compcert.jsonl","session\_id":"019efa71-640d-7060-8c(...TRUNCATED) | null | 1 | 46 | [View Pi session](https://huggingface.co/datasets/AletheiaResearch/GLM-5.2-Bench/blob/main/passed/bench-terminal-bench-2.0-compile-compcert.jsonl "View Pi session")"{\\"type\\": \\"session\\", \\"version\\": 3, \\"id\\": \\"019efa71-640d-7060-8cd3-7ea1bae9b803\\", \\"timesta(...TRUNCATED) | passed/bench-terminal-bench-2.0-compile-compcert.jsonl |\
| pi | 019efa73-82ad-771e-981b-5708e354326e | Configure a git server so that I can run on my computer<br>git clone user@server:/git/server<br>echo "hello world" > hello.html<br>git add hello.html<br>git commit -m "add hello.html"<br>git push origin master<br>And have this data then be pushed to a webserver running on port 8080 so if I run<br>curl http://server:... | \[{"role":"user","content":"Configure a git server so that I can run on my computer\\n git clone us(...TRUNCATED) | \[{"type":"function","function":{"name":"bash","parameters":{"type":"object","properties":{"command":(...TRUNCATED) | {"source\_file":"bench-terminal-bench-2.0-configure-git-webserver.jsonl","session\_id":"019efa73-82ad-(...TRUNCATED) | null | 1 | 11 | [View Pi session](https://huggingface.co/datasets/AletheiaResearch/GLM-5.2-Bench/blob/main/passed/bench-terminal-bench-2.0-configure-git-webserver.jsonl "View Pi session")"{\\"type\\": \\"session\\", \\"version\\": 3, \\"id\\": \\"019efa73-82ad-771e-981b-5708e354326e\\", \\"timesta(...TRUNCATED) | passed/bench-terminal-bench-2.0-configure-git-webserver.jsonl |\
| pi | 019efa76-7d2e-77c8-8130-630592a9960b | Find a 1-hour meeting slot for Alice, Bob, and Carol during January 15-19, 2024 (business hours: 9 AM - 6 PM, Monday-Friday) that satisfies their availability constraints and existing calendar conflicts.<br>Availability & Preferences:<br>\- Alice: Prefers mornings (9 AM - 12 PM), can do early afternoons (12-2 PM) if needed. ... | \[{"role":"user","content":"Find a 1-hour meeting slot for Alice, Bob, and Carol during January 15-19(...TRUNCATED) | \[{"type":"function","function":{"name":"read","parameters":{"type":"object","properties":{"path":{"t(...TRUNCATED) | {"source\_file":"bench-terminal-bench-2.0-constraints-scheduling.jsonl","session\_id":"019efa76-7d2e-7(...TRUNCATED) | null | 1 | 4 | [View Pi session](https://huggingface.co/datasets/AletheiaResearch/GLM-5.2-Bench/blob/main/passed/bench-terminal-bench-2.0-constraints-scheduling.jsonl "View Pi session")"{\\"type\\": \\"session\\", \\"version\\": 3, \\"id\\": \\"019efa76-7d2e-77c8-8130-630592a9960b\\", \\"timesta(...TRUNCATED) | passed/bench-terminal-bench-2.0-constraints-scheduling.jsonl |\
\
End of preview.\
\
This dataset was generated using [teich](https://github.com/TeichAI/teich) by [TeichAI](https://huggingface.co/TeichAI)![](https://cdn-avatars.huggingface.co/v1/production/uploads/6837935ac3b7ffe0d2559ce9/-AxyvV4wfUY8uo87kNKkK.png)\
\
# GLM-5.2 Bench results\
\
This directory contains raw agent trace files generated by teich.\
\
JSONL files: 42\
\
Model metadata: `z-ai/glm-5.2`\
\
## Training-ready tools\
\
Generated agent traces carry configured or recovered tool schemas so tools remain available for training even when a session did not call them.\
Native Claude Code imports recover schemas for Claude Code and Claude Desktop built-ins, plus conservative name-derived MCP schemas, when the raw transcript only records tool names or calls.\
A complete dataset-level `tools` schema snapshot is embedded in the collapsed section at the bottom of this README.\
`load_traces` applies the dataset snapshot to each loaded example as a fallback `tools` field.\
\
## Format\
\
Each file is newline-delimited JSON representing a single captured agent session.\
The trace schema is designed for upload-first preservation so you can keep the original session history and convert it later for training.\
Teich normalizes split assistant fragments during trace copy and conversion so the semantic order is reasoning first, optional assistant text second, and tool calls last.\
Native Claude Code conversion also preserves runtime context such as skills, MCP instructions, hook context, permission state, date changes, and session recaps as masked `system` messages when the raw transcript provides them.\
\
Common top-level event groups:\
\
- `session_meta`\
- `turn_context`\
- `event_msg`\
- `response_item`\
- `session`\
- `message`\
- `session_info`\
- `model_change`\
- `thinking_level_change`\
- `external_session_meta`\
- `external_message`\
- `external_stderr`\
\
## Example\
\
```json\
{"type": "session", "version": 3, "id": "019efa62-91bd-70ce-aa84-f10c2e975189", "timestamp": "2026-06-24T16:07:04.383Z", "cwd": "/app"}\
```\
\
## Training\
\
Use this dataset as `AletheiaResearch/GLM-5.2-Bench` with Teich's data preparation and training utilities.\
If you do not want Teich to handle chat-template formatting or masking, run `teich convert` to write standalone OpenAI-style JSONL rows with `prompt`, `messages`, `tools`, and `metadata`.\
Training setup details evolve over time, so the maintained guide lives in the [Teich training docs](https://github.com/TeichAI/teich/blob/main/docs/training.md).\
For loading, mixing, converting, and validating Teich datasets, see [Preparing Data](https://github.com/TeichAI/teich/blob/main/docs/prepare-data.md).\
\
## Tool schema snapshot\
\
Training-ready tool schema snapshot\
\
```json\
[\
  {\
    "type": "function",\
    "function": {\
      "name": "bash",\
      "description": "Run shell commands in the workspace.",\
      "parameters": {\
        "type": "object",\
        "properties": {\
          "cmd": {\
            "type": "string"\
          },\
          "command": {\
            "type": "string"\
          },\
          "cwd": {\
            "type": "string"\
          },\
          "description": {\
            "type": "string"\
          },\
          "timeout": {\
            "type": "integer"\
          }\
        },\
        "additionalProperties": true\
      }\
    }\
  },\
  {\
    "type": "function",\
    "function": {\
      "name": "edit",\
      "description": "Edit file contents in the workspace.",\
      "parameters": {\
        "type": "object",\
        "properties": {\
          "edits": {\
            "type": "array"\
          },\
          "file_path": {\
            "type": "string"\
          },\
          "path": {\
            "type": "string"\
          }\
        },\
        "additionalProperties": true,\
        "required": [\
          "edits"\
        ]\
      }\
    }\
  },\
  {\
    "type": "function",\
    "function": {\
      "name": "read",\
      "description": "Read file contents from the workspace.",\
      "parameters": {\
        "type": "object",\
        "properties": {\
          "file_path": {\
            "type": "string"\
          },\
          "limit": {\
            "type": "integer"\
          },\
          "offset": {\
            "type": "integer"\
          },\
          "path": {\
            "type": "string"\
          }\
        },\
        "additionalProperties": true\
      }\
    }\
  },\
  {\
    "type": "function",\
    "function": {\
      "name": "read_file",\
      "description": "Read file contents from the workspace.",\
      "parameters": {\
        "type": "object",\
        "properties": {\
          "path": {\
            "type": "string"\
          }\
        },\
        "additionalProperties": true,\
        "required": [\
          "path"\
        ]\
      }\
    }\
  },\
  {\
    "type": "function",\
    "function": {\
      "name": "write",\
      "description": "Write file contents in the workspace.",\
      "parameters": {\
        "type": "object",\
        "properties": {\
          "content": {\
            "type": "string"\
          },\
          "file_path": {\
            "type": "string"\
          },\
          "path": {\
            "type": "string"\
          }\
        },\
        "additionalProperties": true,\
        "required": [\
          "content"\
        ]\
      }\
    }\
  },\
  {\
    "type": "function",\
    "function": {\
      "name": "write_file",\
      "description": "Write file contents in the workspace.",\
      "parameters": {\
        "type": "object",\
        "properties": {\
          "content": {\
            "type": "string"\
          },\
          "path": {\
            "type": "string"\
          }\
        },\
        "additionalProperties": true,\
        "required": [\
          "content",\
          "path"\
        ]\
      }\
    }\
  }\
]\
```\
\
Copy to bucket new\
\
Downloads last month\
\
479\
\
Total file size:\
\
4.36 MB\
\
The table displays a preview with only the first rows.\
\
View Pi Session\
\
View Pi Session\
\
View Pi Session\
\
View Pi Session\
\
View Pi Session\
\
View Pi Session\
\
View Pi Session\
\
View Pi Session\
\
View Pi Session\
\
StripeM-Inner
