from up.base_started_module import BaseStartedModule


class DummyModule(BaseStartedModule):
    def _execute_start(self):
        return True

    def load(self):
        return True
