class AnswerService:
    def __init__(self, prompt_service, completion_service, trace_service):
        self.prompt_service = prompt_service
        self.completion_service = completion_service
        self.trace_service = trace_service

