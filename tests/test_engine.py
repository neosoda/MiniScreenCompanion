import unittest
from PIL import Image
import numpy as np

from src.config import AppConfig, TelemetryConfig
from src.driver.simulator import SimulatorDriver
from src.engine import TuringCompanionEngine


class EngineTests(unittest.TestCase):
    def test_simulator_engine_micro_blit(self):
        config = AppConfig(
            telemetry=TelemetryConfig(interval_sec=0.1, mode="fluid", full_sync_sec=10.0)
        )
        engine = TuringCompanionEngine(config=config, simulate=True)
        self.assertEqual(engine.interval_sec, 0.1)
        self.assertEqual(engine.mode, "fluid")

        # Snapshot collect
        snap = engine._collect_snapshot()
        self.assertIsNotNone(snap.cpu)
        self.assertIsNotNone(snap.ram)
        self.assertIsNotNone(snap.gpu)

        # Render
        img = engine.renderer.render(snap)
        self.assertEqual(img.size, (480, 320))

        # Push full initial
        self.assertTrue(engine.driver.display_pil_image(img))
        self.assertTrue(hasattr(engine.driver, "display_partial"))

        # Partial blit
        partial = img.crop((50, 50, 150, 100))
        self.assertTrue(engine.driver.display_partial(partial, 50, 50))


if __name__ == "__main__":
    unittest.main()
