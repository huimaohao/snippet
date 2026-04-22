# LLM Client

## Provider Interface

### [DashScope](https://github.com/dashscope/dashscope-sdk-python)

- 文档组织混乱，示例代码不友好，不知道哪些接口支持哪些模型，哪些模型支持哪些参数
- 有些模型根本无法使用 `DashScope` 来调用，只能使用兼容 `OpenAI` 的接口来调用
- 参数 `incremental_output` 的名字含义和文档说明，与实际使用效果相反
- 参数 `temperature = 0` 对部分模型无效，而且对其它模型也不是总有效，无法每次得到一致结果
- 参数 `result_format` 不是对所有的模型都有效，例如 `qwen3-max` 只支持 `message` 格式

## Unified Interface

### [Instructor](https://github.com/567-labs/instructor)

- 基于 `Pydantic` 来提供统一的结构化输出的接口
- `llm_validator()` 中的 `client` 参数已经提供过要调用的模型，但仍需再次传递 `model` 参数

### [LangChain](https://github.com/langchain-ai/langchain)

- 使用 `langchain_openai.ChatOpenAI` 调用 `qwen` 模型时，响应的 `message` 中缺少推理内容
- 官方的 `langchain_community` 中的 `ChatTongyi` 基于 `DashScope` 实现，虽然传入参数 `model_kwargs={"enable_thinking": True}`，但是仍然存在上述问题
- 非官方的 `langchain_qwq.ChatQwen` 基于 `langchain_openai.ChatOpenAI` 实现，所以也存在上述问题

### [LiteLLm](https://github.com/BerriAI/litellm)

- 试图为不同厂家的不同模型提供统一的与 `OpenAI` 相同格式的接口
- 受限于不同模型的能力，新模型的不断出现，适配速度不够及时，以及文档不够全面，在使用中仍感觉很鸡肋
- 使用 `Ollama` 作为后端时，`Responses API` 结果有错，猜测是使用其它接口加结构化输出的方式来实现的

### [Ollama](https://github.com/ollama/ollama-python)

- 未提供类似 `OpenAI` 的 `Responses API`，且底层不完全支持 `OpenAI` 的 `Responses API`
- 任何把 `Ollama` 作为后端的中转库，其提供的 `Responses API` 都是使用其它接口变相实现的

---

## Reference

### Provider Interface

- [DashScope](https://github.com/dashscope/dashscope-sdk-python)
- [OpenAI](https://github.com/openai/openai-python)

### Unified Interface

- [Instructor](https://github.com/567-labs/instructor)
- [LangChain](https://github.com/langchain-ai/langchain)
- [LiteLLm](https://github.com/BerriAI/litellm)
- [Ollama](https://github.com/ollama/ollama-python)
