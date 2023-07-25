import io

class PSRestResponseStream(io.BytesIO):
    def __init__(self, response):
        super().__init__(response.content)
        self.response = response
        self._is_closed = False

    def close(self):
        if not self._is_closed:
            self.response.close()
            self._is_closed = True
        super().close()

    def __del__(self):
        self.close()

    