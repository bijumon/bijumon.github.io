## user
whats the total download size of 
Qwen2.5-Coder-32B-Instruct-GGUF 
## assistant

The total download size of the Qwen2.5-Coder-32B-Instruct-GGUF model varies depending on the quantization format you choose. Here are the available formats and their corresponding sizes:

### Quantization Formats and Sizes

| Format           | Size    |
|------------------|---------|
| **Q8_0**         | 34.82 GB |
| **Q6_K_L**       | 27.26 GB |
| **Q6_K**         | 26.89 GB |
| **Q5_K_L**       | 23.74 GB |
| **Q5_K_M**       | 23.26 GB |
| **Q5_K_S**       | 22.64 GB |
| **Q4_K_L**       | 20.43 GB |
| **Q4_K_M**       | 19.85 GB |
| **Q4_K_S**       | 18.78 GB |
| **Q4_0**         | 18.71 GB |
| **IQ4_NL**       | 18.68 GB |
| **Q4_0_8_8**     | 18.64 GB |
| **Q4_0_4_8**     | 18.64 GB |
| **Q4_0_4_4**     | 18.64 GB |
| **Q3_K_XL**      | 17.93 GB |
| **IQ4_XS**       | 17.69 GB |
| **Q3_K_L**       | 17.25 GB |
| **Q3_K_M**       | 15.94 GB |
| **IQ3_M**        | 14.81 GB |
| **Q3_K_S**       | 14.39 GB |
| **IQ3_XS**       | 13.71 GB |
| **Q2_K_L**       | 13.07 GB |
| **IQ3_XXS**      | 12.84 GB |
| **Q2_K**         | 12.31 GB |
| **IQ2_M**        | 11.26 GB |
| **IQ2_S**        | 10.39 GB |
| **IQ2_XS**       | 9.96 GB  |
| **IQ2_XXS**      | 9.03 GB  |

These sizes are for individual quantized files. If you intend to download the entire model, you can use the Hugging Face CLI to fetch all files:


```bash
huggingface-cli download bartowski/Qwen2.5-Coder-32B-Instruct-GGUF --include "Qwen2.5-Coder-32B-Instruct-Q8_0/*" --local-dir ./
```


This command will download all files related to the Q8_0 quantization format into the current directory. Ensure you have sufficient storage space, as the total size can be substantial.

If you need further assistance with the download process or have other questions, feel free to ask! 