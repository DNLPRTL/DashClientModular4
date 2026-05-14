# Baseline Signal Matrix

| signal | unit | rate_based | bba | bola | mpc | robust_mpc | sanity_controllers | exists_in_client | telemetry_source | derivation | risk | decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| representation_rates | bytes_per_second_list | required | required | required | required | required | required | yes | `rates` | MPD representation ladder sorted by player | codec/adaptation-set equivalence must be checked later | use |
| selected_level | representation_index | required | required | required | required | required | required | yes | `level` | current player level | none for controller input | use |
| max_selectable_level | representation_index | guard | guard | guard | guard | guard | required | yes | `max_level` | ladder upper bound | none | use |
| min_representation_rate | bytes_per_second | optional | optional | optional | optional | optional | required | yes | `min_rate` | min of ladder | legacy aliases also exist | use for sanity |
| max_representation_rate | bytes_per_second | optional | optional | optional | optional | optional | required | yes | `max_rate` | max of ladder | legacy aliases also exist | use for sanity |
| buffer_seconds | seconds | optional safety | primary | primary | primary | primary | optional | yes | `queued_time` | media engine queued time | fake/GStreamer equivalence not claimed | use with method note |
| buffer_bytes_estimate | bytes | no | optional | optional | no | no | no | yes | `queued_bytes` | media engine queued bytes | engine-dependent | do not use initially |
| last_fragment_size_bytes | bytes | required | no | no | required | required | no | yes | `last_fragment_size` | downloader/player measurement | retries and init rows need rules | use after spec |
| last_download_time_seconds | seconds | required | no | no | required | required | no | yes | `last_download_time` | downloader timing | retries and timing semantics need rules | use after spec |
| measured_download_rate | bytes_per_second | required | no | no | required | required | no | yes | `bwe`, `tp_now` | last size divided by last time or fallback | `bwe` is legacy naming and fallback-based | derive explicitly |
| throughput_history | bytes_per_second_list | required | no | no | required | required | no | partial | telemetry rows / controller state | collect measured download rates over segments | controller state must be deterministic | implement in controller/spec later |
| throughput_prediction | bytes_per_second | no | no | no | required | required | no | no direct field | controller state | predictor from throughput history | exact predictor must be specified | defer to MPC specs |
| prediction_error_history | ratio_or_fraction | no | no | no | optional | required | no | no direct field | controller state | compare predicted vs observed throughput over past chunks | robustMPC definition must be pinned down | defer to robustMPC spec |
| segment_duration_seconds | seconds | optional | optional | required | required | required | no | yes | `fragment_duration` | parser/player duration context | init rows use zero | use for media rows |
| segment_index | index | optional | optional | optional | required | required | optional | yes | `segment_index` | player segment index | sequence semantics must stay reproducible | use |
| utility_function | dimensionless | no | no | required | required | required | no | no | spec | usually derived from bitrate or quality model | source-specific and QoE-sensitive | defer |
| qoe_reward_weights | formula parameters | no | no | optional | required | required | no | no | methodology | quality/rebuffer/switch penalty weights | final QoE is explicitly deferred | block MPC until resolved |
| idle_duration | seconds | optional | no | possible | possible | possible | no | API exists | `getIdleDuration()` | controller return path | semantics not part of current science block | defer |
| stall_signal | seconds_or_boolean | no | no | evaluation only | evaluation only | evaluation only | no | partial | `stall_flag`, `stall_duration` | media event aggregation | final QoE interpretation not defined | do not use as final reward yet |
| device_or_user_context | mixed | no | no | no | no | no | no | no | none | would require new data | out of initial scope | exclude |
| content_complexity | mixed | no | no | no | no | no | no | no | none | would require media/content analysis | out of initial scope | exclude |
