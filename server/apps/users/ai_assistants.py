from django_ai_assistant import AIAssistant, method_tool


class PersonalAIAssistant(AIAssistant):
    id = 'personal_assistant'
    name = 'Personal Assistant'
    instructions = 'You are a personal assistant.'
    model = 'gpt-4o'

    @method_tool
    def get_current_user_username(self) -> str:
        """Get the username of the current user"""
        return self._user.username


# Register the assistant
# personal_ai_assistant = PersonalAIAssistant()
