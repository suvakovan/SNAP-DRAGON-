# Measured NPU vs CPU Benchmark Diagnostics

**Last Run Timestamp:** 20260928_170845

## Methodology

- **Protocol:** 2 warmup runs, followed by measured iterations.
- **Environment:** Windows 11 ARM64 Native Python Environment.
- **Verification:** `verified_npu` is marked True strictly when hardware execution provider (QNN HTP) is verified active.

## Benchmark Results Table

| task   | backend         | device   | verified_npu   |   mean_wall_sec |     mean_rtf |   std_rtf |   mean_cpu_percent |   mean_latency_sec |   mean_tps |   std_tps |
|:-------|:----------------|:---------|:---------------|----------------:|-------------:|----------:|-------------------:|-------------------:|-----------:|----------:|
| STT    | onnxruntime-cpu | CPU      | False          |       0.0507243 |   0.00169081 |         0 |               33.3 |                nan |        nan |       nan |
| STT    | onnxruntime-cpu | CPU      | False          |       0.0509765 |   0.00169922 |         0 |               29.2 |                nan |        nan |       nan |
| LLM    | cpu-fallback    | CPU      | False          |     nan         | nan          |       nan |                0   |                  0 |       3200 |         0 |
| LLM    | cpu-fallback    | CPU      | False          |     nan         | nan          |       nan |                0   |                  0 |       3200 |         0 |

