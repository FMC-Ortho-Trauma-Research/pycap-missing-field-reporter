class Pipeline:
    def __init__(self, loader, transformer, parser, reporter):
        self.loader = loader
        self.transformer = transformer
        self.parser = parser
        self.reporter = reporter

    def run(self):
        raise NotImplementedError
