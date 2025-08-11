## user
what is tiny-vicuna
## assistant

Tiny-Vicuna-1B is a compact and efficient open-source language model designed to deliver strong performance on limited hardware. It is a fine-tuned version of the TinyLlama 1.1B model, trained on the WizardVicuna dataset, and is fully compatible with the Vicuna-v1.5 series citeturn0search0.

### 🔍 Key Features

- **Model Size**: Approximately 1.1 billion parameters.
- **Memory Efficiency**: Requires less than 700 MB of RAM, making it suitable for devices with limited resources citeturn0search1.
- **Training Dataset**: Fine-tuned on the WizardVicuna dataset, enhancing its instruction-following capabilities.
- **Quantization Options**: Available in various quantized formats (e.g., q2_k, q3_k_m, q4_k_m, q5_k_m, q6_k, q8_0) to balance performance and resource usage citeturn0search8.

### 🧠 Performance Benchmarks

According to evaluations on the Open LLM Leaderboard, Tiny-Vicuna-1B achieves the following scores:

- **HellaSwag (10-shot)**: 55.92
- **Winogrande (5-shot)**: 58.41
- **TruthfulQA (0-shot)**: 33.82
- **AI2 Reasoning Challenge (25-shot)**: 33.45
- **MMLU (5-shot)**: 25.45
- **GSM8k (5-shot)**: 1.52
- **Average Score**: 34.76

These results indicate that while Tiny-Vicuna-1B may not match the performance of larger models, it offers a commendable balance between size and capability citeturn0search0.

### ⚙️ Use Cases

Tiny-Vicuna-1B is well-suited for a variety of applications, especially where computational resources are limited:

- **Mobile and Edge Devices**: Its small footprint allows deployment on smartphones and other low-power devices.
- **Education and Research**: Ideal for environments with constrained hardware, facilitating learning and experimentation.
- **Content Generation**: Capable of tasks like summarization, question answering, and formatting outputs citeturn0search6.

### 🚀 Getting Started

To run Tiny-Vicuna-1B locally:

1. **Set Up Environment**:
   - Create and activate a Python virtual environment.
   - Install necessary packages:
     ```bash
     pip install llama-cpp-python gradio psutil plotly
     ```

2. **Download Model**:
   - Obtain the quantized model file (e.g., `tiny-vicuna-1b.q5_k_m.gguf`) from the [Hugging Face repository](https://huggingface.co/afrideva/Tiny-Vicuna-1B-GGUF).

3. **Run the Model**:
   - Use the following Python code to load and interact with the model:
     ```python
     from llama_cpp import Llama

     modelfile = "./tiny-vicuna-1b.q5_k_m.gguf"
     llm = Llama(model_path=modelfile, n_ctx=2048)

     prompt = "USER: What is the meaning of life? ASSISTANT:"
     response = llm(prompt)
     print(response)
     ```

For more detailed instructions and examples, refer to the [Anakin.ai blog post](https://anakin.ai/blog/tiny-vicuna-1b/).

### 📥 Where to Access

- **Model Repository**: [Jiayi-Pan/Tiny-Vicuna-1B on Hugging Face](https://huggingface.co/Jiayi-Pan/Tiny-Vicuna-1B)
- **Quantized Versions**: [afrideva/Tiny-Vicuna-1B-GGUF on Hugging Face](https://huggingface.co/afrideva/Tiny-Vicuna-1B-GGUF)

Tiny-Vicuna-1B represents a significant step towards making AI more accessible, offering a practical solution for applications where resources are limited. 