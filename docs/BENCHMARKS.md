# Measured NPU vs CPU Benchmark Diagnostics

**Last Run Timestamp:** 20260928_165937

## Methodology

- **Protocol:** 2 warmup runs, followed by measured iterations.
- **Environment:** Windows 11 ARM64 Native Python Environment.
- **Verification:** `verified_npu` is marked True strictly when hardware execution provider (QNN HTP) is verified active.

## Benchmark Results Table

| task   | backend         | device   | verified_npu   |   mean_wall_sec |     mean_rtf |   std_rtf |   mean_cpu_percent |   mean_latency_sec |   mean_tps |   std_tps |
|:-------|:----------------|:---------|:---------------|----------------:|-------------:|----------:|-------------------:|-------------------:|-----------:|----------:|
| STT    | onnxruntime-cpu | CPU      | False          |       0.0507388 |   0.00169129 |         0 |               25   |                nan |        nan |       nan |
| STT    | onnxruntime-cpu | CPU      | False          |       0.0509386 |   0.00169795 |         0 |               17.2 |                nan |        nan |       nan |
| LLM    | cpu-fallback    | CPU      | False          |     nan         | nan          |       nan |                0   |                  0 |       3200 |         0 |
| LLM    | cpu-fallback    | CPU      | False          |     nan         | nan          |       nan |                0   |                  0 |       3200 |         0 |

