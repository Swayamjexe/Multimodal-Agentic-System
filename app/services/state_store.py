from app.models.state import AgentState

class StateStore:
    sessions = {}

    @staticmethod
    def get(session_id: str) -> AgentState:
        if session_id not in StateStore.sessions:
            StateStore.sessions[session_id] = AgentState()
        return StateStore.sessions[session_id]

    @staticmethod
    def update(session_id: str, state: AgentState):
        StateStore.sessions[session_id] = state
