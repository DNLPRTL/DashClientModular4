from __future__ import annotations

import importlib
import logging
import unittest
from unittest import mock

import main as main_module
from core.client_config import ClientConfig
from core.media_engine import gst_media_engine


class FakePad:
    def __init__(self):
        self.linked = False

    def is_linked(self):
        return self.linked


class FakeElement:
    def __init__(self, factory_name, instance_name):
        self.factory_name = factory_name
        self.instance_name = instance_name
        self.properties = {}
        self.link_result = True

    def set_property(self, name, value):
        self.properties[name] = value

    def connect(self, *args):
        return None

    def link(self, other):
        return self.link_result

    def get_static_pad(self, name):
        return FakePad()

    def get_name(self):
        return self.instance_name


class FakeBus:
    def add_signal_watch(self):
        return None

    def connect(self, *args):
        return None


class FakePipeline(FakeElement):
    def __init__(self, name):
        super().__init__("pipeline", name)
        self.elements = []
        self.states = []

    def add(self, element):
        self.elements.append(element)

    def get_bus(self):
        return FakeBus()

    def set_state(self, state):
        self.states.append(state)


class FakeGst:
    init_calls = []

    class Format:
        TIME = "time"

    class State:
        NULL = "null"
        PAUSED = "paused"

    class MessageType:
        EOS = "eos"
        ERROR = "error"
        STATE_CHANGED = "state-changed"
        QOS = "qos"
        BUFFERING = "buffering"
        LATENCY = "latency"

    class Pipeline:
        @staticmethod
        def new(name):
            return FakePipeline(name)

    class ElementFactory:
        calls = []
        missing = set()

        @classmethod
        def make(cls, factory_name, instance_name):
            cls.calls.append(factory_name)
            if factory_name in cls.missing:
                return None
            return FakeElement(factory_name, instance_name)

    @staticmethod
    def init(args):
        FakeGst.init_calls.append(args)


class FakeGLib:
    source_remove_calls = []

    class MainLoop:
        def run(self):
            return None

        def quit(self):
            return None

        def is_running(self):
            return False

    @staticmethod
    def timeout_add(interval_ms, callback):
        return 1

    @staticmethod
    def source_remove(source_id):
        FakeGLib.source_remove_calls.append(source_id)


class FakeErrorMessage:
    type = FakeGst.MessageType.ERROR

    def __init__(self):
        self.src = FakeElement("source", "test-source")

    def parse_error(self):
        return RuntimeError("boom"), "debug detail"


class GstMediaEngineContractTest(unittest.TestCase):
    def setUp(self):
        self._logging_disable_level = logging.root.manager.disable
        logging.disable(logging.CRITICAL)
        FakeGst.ElementFactory.calls = []
        FakeGst.ElementFactory.missing = set()
        FakeGst.init_calls = []
        FakeGLib.source_remove_calls = []

    def tearDown(self):
        logging.disable(self._logging_disable_level)

    def _patch_fake_gst(self):
        return mock.patch.multiple(
            gst_media_engine,
            GST_AVAILABLE=True,
            GST_IMPORT_ERROR=None,
            Gst=FakeGst,
            GLib=FakeGLib,
        )

    def test_module_import_is_safe_without_requiring_gstreamer(self):
        module = importlib.import_module("core.media_engine.gst_media_engine")

        self.assertTrue(hasattr(module, "GstMediaEngine"))
        self.assertTrue(hasattr(module, "GST_AVAILABLE"))

    def test_config_can_select_gst_without_requiring_gstreamer(self):
        config = ClientConfig.from_dict(
            {
                "mpd_url": "http://example.invalid/video.mpd",
                "media_engine": {
                    "name": "gst",
                    "min_queue_time": 1.5,
                    "decode_video": True,
                    "sink_name": "autovideosink",
                },
            }
        )

        self.assertEqual("gst", config.media_engine.name)
        self.assertEqual(1.5, config.media_engine.min_queue_time)
        self.assertTrue(config.media_engine.decode_video)
        self.assertEqual("autovideosink", config.media_engine.sink_name)

    def test_missing_gstreamer_error_explains_safe_fallback_and_validation(self):
        with mock.patch.multiple(
            gst_media_engine,
            GST_AVAILABLE=False,
            GST_IMPORT_ERROR=ModuleNotFoundError("No module named 'gi'"),
        ):
            with self.assertRaisesRegex(RuntimeError, "GStreamer/PyGObject is unavailable") as ctx:
                gst_media_engine.GstMediaEngine()

        message = str(ctx.exception)
        self.assertIn("media_engine.name: fake", message)
        self.assertIn("check_environment.py --profile gst --strict", message)
        self.assertIn("Windows does not require GStreamer", message)

    def test_main_gst_selection_uses_clear_unavailable_message(self):
        config = ClientConfig.from_dict(
            {
                "mpd_url": "http://example.invalid/video.mpd",
                "media_engine": {"name": "gst"},
            }
        )

        with mock.patch.object(main_module, "GST_AVAILABLE", False):
            with mock.patch.object(main_module, "GstMediaEngine", None):
                with mock.patch.object(
                    main_module,
                    "gstreamer_unavailable_message",
                    return_value="clear gst unavailable",
                ):
                    with self.assertRaisesRegex(main_module.ConfigError, "clear gst unavailable"):
                        main_module._create_media_engine(config)

    def test_headless_default_selects_fakesink_without_visible_playback(self):
        with self._patch_fake_gst():
            engine = gst_media_engine.GstMediaEngine(decode_video=False, sink_name=None)

        self.assertEqual("fakesink", engine.sink_name)
        self.assertFalse(engine.visible_playback)

    def test_missing_decoder_names_required_element(self):
        FakeGst.ElementFactory.missing = {"avdec_h264"}

        with self._patch_fake_gst():
            engine = gst_media_engine.GstMediaEngine(decode_video=True)
            with self.assertRaisesRegex(RuntimeError, "avdec_h264") as ctx:
                engine.start()

        self.assertIn("Required GStreamer element 'avdec_h264'", str(ctx.exception))
        self.assertIn("check_environment.py --profile gst --strict", str(ctx.exception))

    def test_explicit_missing_sink_does_not_fallback_to_fakesink(self):
        FakeGst.ElementFactory.missing = {"waylandsink"}

        with self._patch_fake_gst():
            engine = gst_media_engine.GstMediaEngine(decode_video=True, sink_name="waylandsink")
            with self.assertRaisesRegex(RuntimeError, "waylandsink") as ctx:
                engine.start()

        self.assertIn("explicit media_engine.sink_name", str(ctx.exception))
        self.assertNotIn("fakesink", FakeGst.ElementFactory.calls)

    def test_link_failure_raises_runtime_error_instead_of_assert(self):
        src = FakeElement("appsrc", "src")
        dst = FakeElement("qtdemux", "demux")
        src.link_result = False

        with self.assertRaisesRegex(RuntimeError, "appsrc->qtdemux"):
            gst_media_engine.GstMediaEngine._link_or_raise(src, dst, "appsrc", "qtdemux")

    def test_bus_error_event_includes_source_and_debug(self):
        with self._patch_fake_gst():
            engine = gst_media_engine.GstMediaEngine(decode_video=False)
            events = []
            engine.on_event = lambda event, info: events.append((event, info))
            engine._on_bus_message(None, FakeErrorMessage())

        self.assertEqual(1, len(events))
        event, info = events[0]
        self.assertEqual("error", event)
        self.assertEqual("test-source", info["source"])
        self.assertEqual("boom", info["error"])
        self.assertEqual("debug detail", info["debug"])

    def test_stop_is_idempotent(self):
        with self._patch_fake_gst():
            engine = gst_media_engine.GstMediaEngine(decode_video=False)
            engine.stop()
            engine.stop()

        self.assertIsNone(engine.pipeline)


if __name__ == "__main__":
    unittest.main()
