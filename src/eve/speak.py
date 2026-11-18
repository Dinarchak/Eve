import threading
import sounddevice as sd
from piper import PiperVoice


class Speaker:
    def __init__(self, model_path: str):
        # Модель загружается один раз — это дорогая операция
        self.voice = PiperVoice.load(model_path)
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def speak(self, text: str, blocking: bool = True):
        """Синтезирует и проигрывает текст. Можно прервать через stop()."""
        self.stop()  # остановить предыдущую озвучку, если была
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._play, args=(text,), daemon=True)
        self._thread.start()
        if blocking:
            self._thread.join()

    def _play(self, text: str):
        stream_iter = self.voice.synthesize(text)
        try:
            first = next(stream_iter, None)
            if first is None:
                return
            with sd.RawOutputStream(
                samplerate=first.sample_rate,
                channels=first.sample_channels,
                dtype="int16",
            ) as out:
                out.write(first.audio_int16_bytes)
                for chunk in stream_iter:
                    if self._stop_event.is_set():
                        break
                    out.write(chunk.audio_int16_bytes)
        finally:
            stream_iter.close()  # освобождаем генератор Piper

    def stop(self):
        """Прерывает текущую озвучку (например, когда пользователь заговорил)."""
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join()

speaker = Speaker('D:/Projects/Eve/ru_RU-irina-medium.onnx')

speaker.speak("Привет, это тест Piper")           # блокирующе
speaker.speak("Долгий текст", blocking=False)  # в фоне
# ...пользователь заговорил:
speaker.stop()     