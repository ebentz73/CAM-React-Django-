import rest_framework.response


class ResponseThen(rest_framework.response.Response):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.then = None
        self.then_args = ()
        self.then_kwargs = {}

    def close(self):
        super().close()
        if self.then:
            self.then(*self.then_args, **self.then_kwargs)


rest_framework.response.Response = ResponseThen
