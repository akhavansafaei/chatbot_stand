"""LLM (Large Language Model) module with multiple provider options."""

from typing import AsyncGenerator, List, Dict
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def generate(self, messages: List[Dict[str, str]]) -> str:
        """Generate a response from messages.

        Args:
            messages: List of message dictionaries with 'role' and 'content'

        Returns:
            Generated response text
        """
        pass

    @abstractmethod
    async def generate_stream(self, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        """Generate a streaming response from messages.

        Args:
            messages: List of message dictionaries with 'role' and 'content'

        Yields:
            Generated response chunks
        """
        pass


class OpenAILLM(LLMProvider):
    """OpenAI LLM provider."""

    def __init__(self, api_key: str, model: str = "gpt-4o", temperature: float = 0.7,
                 max_tokens: int = 2000):
        """Initialize OpenAI LLM.

        Args:
            api_key: OpenAI API key
            model: Model name
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
        """
        try:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=api_key)
            self.model = model
            self.temperature = temperature
            self.max_tokens = max_tokens
        except ImportError:
            raise ImportError("Please install openai: pip install openai")

    async def generate(self, messages: List[Dict[str, str]]) -> str:
        """Generate a response from messages.

        Args:
            messages: List of message dictionaries

        Returns:
            Generated response text
        """
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )

        return response.choices[0].message.content

    async def generate_stream(self, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        """Generate a streaming response from messages.

        Args:
            messages: List of message dictionaries

        Yields:
            Generated response chunks
        """
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stream=True
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class GoogleLLM(LLMProvider):
    """Google Gemini LLM provider."""

    def __init__(self, api_key: str, model: str = "gemini-1.5-pro", temperature: float = 0.7,
                 max_tokens: int = 2000):
        """Initialize Google Gemini LLM.

        Args:
            api_key: Google API key
            model: Model name
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
        """
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.model_name = model
            self.model = genai.GenerativeModel(model)
            self.temperature = temperature
            self.max_tokens = max_tokens
            self.genai = genai
        except ImportError:
            raise ImportError("Please install google-generativeai: pip install google-generativeai")

    def _convert_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Convert OpenAI-style messages to Gemini format.

        Args:
            messages: List of message dictionaries

        Returns:
            Converted messages for Gemini
        """
        gemini_messages = []
        system_message = None

        for msg in messages:
            role = msg["role"]
            content = msg["content"]

            if role == "system":
                system_message = content
            elif role == "user":
                gemini_messages.append({"role": "user", "parts": [content]})
            elif role == "assistant":
                gemini_messages.append({"role": "model", "parts": [content]})

        # Prepend system message to first user message if exists
        if system_message and gemini_messages:
            if gemini_messages[0]["role"] == "user":
                gemini_messages[0]["parts"][0] = f"{system_message}\n\n{gemini_messages[0]['parts'][0]}"

        return gemini_messages

    async def generate(self, messages: List[Dict[str, str]]) -> str:
        """Generate a response from messages.

        Args:
            messages: List of message dictionaries

        Returns:
            Generated response text
        """
        gemini_messages = self._convert_messages(messages)

        # For single-turn conversation
        if len(gemini_messages) == 1:
            response = await self.model.generate_content_async(
                gemini_messages[0]["parts"][0],
                generation_config=self.genai.GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=self.max_tokens
                )
            )
            return response.text

        # For multi-turn conversation
        chat = self.model.start_chat(history=gemini_messages[:-1])
        response = await chat.send_message_async(
            gemini_messages[-1]["parts"][0],
            generation_config=self.genai.GenerationConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_tokens
            )
        )
        return response.text

    async def generate_stream(self, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        """Generate a streaming response from messages.

        Args:
            messages: List of message dictionaries

        Yields:
            Generated response chunks
        """
        gemini_messages = self._convert_messages(messages)

        # For single-turn conversation
        if len(gemini_messages) == 1:
            response = await self.model.generate_content_async(
                gemini_messages[0]["parts"][0],
                generation_config=self.genai.GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=self.max_tokens
                ),
                stream=True
            )
            async for chunk in response:
                if chunk.text:
                    yield chunk.text
        else:
            # For multi-turn conversation
            chat = self.model.start_chat(history=gemini_messages[:-1])
            response = await chat.send_message_async(
                gemini_messages[-1]["parts"][0],
                generation_config=self.genai.GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=self.max_tokens
                ),
                stream=True
            )
            async for chunk in response:
                if chunk.text:
                    yield chunk.text


class LLMModule:
    """Main LLM module that manages different providers."""

    def __init__(self, config: dict, system_prompt: str = ""):
        """Initialize LLM module.

        Args:
            config: LLM configuration dictionary
            system_prompt: System prompt for the conversation
        """
        self.config = config
        self.system_prompt = system_prompt
        self.provider = self._create_provider()
        self.conversation_history: List[Dict[str, str]] = []

        if system_prompt:
            self.conversation_history.append({
                "role": "system",
                "content": system_prompt
            })

    def _create_provider(self) -> LLMProvider:
        """Create LLM provider based on configuration.

        Returns:
            LLM provider instance
        """
        provider_name = self.config.get("provider", "openai")

        if provider_name == "openai":
            openai_config = self.config.get("openai", {})
            return OpenAILLM(
                api_key=openai_config.get("api_key"),
                model=openai_config.get("model", "gpt-4o"),
                temperature=openai_config.get("temperature", 0.7),
                max_tokens=openai_config.get("max_tokens", 2000)
            )
        elif provider_name == "google":
            google_config = self.config.get("google", {})
            return GoogleLLM(
                api_key=google_config.get("api_key"),
                model=google_config.get("model", "gemini-1.5-pro"),
                temperature=google_config.get("temperature", 0.7),
                max_tokens=google_config.get("max_tokens", 2000)
            )
        else:
            raise ValueError(f"Unknown LLM provider: {provider_name}")

    def add_user_message(self, content: str):
        """Add a user message to conversation history.

        Args:
            content: User message content
        """
        self.conversation_history.append({
            "role": "user",
            "content": content
        })

    def add_assistant_message(self, content: str):
        """Add an assistant message to conversation history.

        Args:
            content: Assistant message content
        """
        self.conversation_history.append({
            "role": "assistant",
            "content": content
        })

    async def generate(self, user_message: str) -> str:
        """Generate a response to a user message.

        Args:
            user_message: User's message

        Returns:
            Generated response
        """
        self.add_user_message(user_message)
        response = await self.provider.generate(self.conversation_history)
        self.add_assistant_message(response)
        return response

    async def generate_stream(self, user_message: str) -> AsyncGenerator[str, None]:
        """Generate a streaming response to a user message.

        Args:
            user_message: User's message

        Yields:
            Generated response chunks
        """
        self.add_user_message(user_message)

        full_response = ""
        async for chunk in self.provider.generate_stream(self.conversation_history):
            full_response += chunk
            yield chunk

        self.add_assistant_message(full_response)

    def clear_history(self):
        """Clear conversation history except system prompt."""
        if self.system_prompt:
            self.conversation_history = [self.conversation_history[0]]
        else:
            self.conversation_history = []
