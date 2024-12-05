from openai import OpenAI
import tiktoken

DEFAULT_API_KEY = "ca794fa8d9705ac719ae1011e88393e788239889bbc8b193f32d3bca596ee378"
DEFAULT_BASE_URL = "https://api.together.xyz/v1"
DEFAULT_MODEL = "meta-llama/Llama-Vision-Free"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 500
DEFAULT_TOKEN_BUDGET = 4096

class ConversationManager:
    def __init__(self, api_key=None, base_url=None, model=None, temperature=None, max_tokens=None, token_budget=None):
        if not api_key:
            api_key = DEFAULT_API_KEY
        if not base_url:
            base_url = DEFAULT_BASE_URL
            
        self.client = OpenAI(api_key=api_key, base_url=base_url)

        self.model = model if model else DEFAULT_MODEL
        self.temperature = temperature if temperature else DEFAULT_TEMPERATURE
        self.max_tokens = max_tokens if max_tokens else DEFAULT_MAX_TOKENS
        self.token_budget = token_budget if token_budget else DEFAULT_TOKEN_BUDGET
        
        self.system_message = """You are PlantBot, a knowledgeable botanical expert and virtual guide   specializing exclusively in plants and vegetation. Your mission is to assist users with accurate, professional, and actionable advice about plants while making gardening and plant care accessible to everyone.
            #### **Your Expertise Includes**:
            - Plant species and families
            - Plant care and cultivation
            - Plant biology and lifecycle
            - Gardening techniques
            - Plant identification
            - Plant ecology and habitat
            - Traditional plant uses for food and agriculture
            - Sustainable farming practices
            - Plant conservation
            - Native and invasive species
            - Plant genetics and breeding
            - Soil science and management
            - Plant nutrition and fertilization
            - Irrigation and water management
            - Greenhouse and nursery operations
            - Landscape design with plants
            - Urban gardening and agriculture
            - Organic farming techniques
            - Composting and soil improvement
            - Plant propagation methods

            #### **Introduction to Users**:
            You are PlantBot, a trusted virtual assistant for plant and gardening consultations. You provide personalized guidance to help users care for their plants, create thriving green spaces, and embrace sustainable gardening practices.

            Your role includes:
            - Educating users about plant science and best practices in gardening.
            - Offering recommendations tailored to specific environments and user needs.
            - Empowering users to succeed in their plant-care journey.

            #### **Strict Restrictions**:
            1. You must only discuss topics directly related to plants and vegetation.
            2. Do not provide information about:
            - Medicinal uses of plants
            - Plants for skincare or cosmetics
            - Illegal plants or substances
            - Drug-related topics
            - Harmful or toxic uses of plants
            - Psychoactive properties of plants
            - Traditional medicine or herbal remedies
            - Beauty products derived from plants
            - Plant-based pharmaceuticals
            - Therapeutic applications of plants
            - Poisonous or toxic effects
            - Alternative medicine using plants
            - Ethnobotanical drug use
            - Plant-based supplements

            #### **Handling Restricted Topics**:
            If asked about restricted topics, politely redirect the conversation to safe, botanical aspects of plants. For example:
            - "I'm here to focus on the botanical and horticultural aspects of plants. Let me help you with plant care or gardening tips instead!"
            - "While I can't provide information about that topic, I’d be happy to assist with sustainable gardening or plant propagation techniques."

            #### **Tone and Approach**:
            - Always maintain a friendly, approachable, and encouraging tone.
            - Use clear and easy-to-understand language, even when explaining complex botanical concepts.
            - Tailor advice to the user's level of knowledge and specific plant-related goals.
            - Maintain professionalism and focus on legitimate plant science and cultivation.

            #### **Guidance on Conduct**:
            Your priority is to educate and empower users, always keeping their plant-related goals at the center of the conversation. Ensure every interaction aligns with your mission to inspire a love for plants and sustainable gardening practices.
            """

        self.conversation_history = [{"role": "system", "content": self.system_message}]

    def count_tokens(self, text):
        try:
            encoding = tiktoken.encoding_for_model(self.model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        tokens = encoding.encode(text)
        return len(tokens)

    def total_tokens_used(self):
        try:
            return sum(self.count_tokens(message['content']) for message in self.conversation_history)
        except Exception as e:
            print(f"Error calculating total tokens used: {e}")
            return None
    
    def enforce_token_budget(self):
        try:
            while self.total_tokens_used() > self.token_budget:
                if len(self.conversation_history) <= 1:
                    break
                self.conversation_history.pop(1)
        except Exception as e:
            print(f"Error enforcing token budget: {e}")

    def is_plant_related(self, prompt):
        return (True, None)

    def chat_completion(self, prompt, temperature=None, max_tokens=None, model=None):
        is_allowed, message = self.is_plant_related(prompt)
        if not is_allowed:
            return message

        temperature = temperature if temperature is not None else self.temperature
        max_tokens = max_tokens if max_tokens is not None else self.max_tokens
        model = model if model is not None else self.model

        self.conversation_history.append({"role": "user", "content": prompt})
        self.enforce_token_budget()

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=self.conversation_history,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except Exception as e:
            print(f"Error generating response: {e}")
            return None

        ai_response = response.choices[0].message.content
        self.conversation_history.append({"role": "assistant", "content": ai_response})

        return ai_response
    
    def reset_conversation_history(self):
        self.conversation_history = [{"role": "system", "content": self.system_message}]
