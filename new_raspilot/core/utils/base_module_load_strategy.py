class BaseModuleLoadStrategy:
    @staticmethod
    def load(module):
        print('Using BaseModuleLoadStrategy')
        return module.load()
