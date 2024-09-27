import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


class ProtocBasicTests(unittest.TestCase):

    tests_dir = Path(__file__).parent.absolute()

    def test_version(self):
        """Test basic calling of `protoc` executable."""
        output = subprocess.run(
            ["protoc", "--version"], check=True, capture_output=True
        )
        self.assertEqual(0, output.returncode)
        self.assertGreater(len(output.stdout), 5)

    def test_compile(self):
        """Test compilation with `protoc`."""
        proto_file = self.tests_dir / "example.proto"

        with TemporaryDirectory() as temp:
            temp = Path(temp)
            output = subprocess.run(
                [
                    "protoc",
                    "--proto_path",
                    str(self.tests_dir),
                    "--python_out",
                    str(temp),
                    proto_file,
                ],
                check=True,
                capture_output=True,
            )
            self.assertEqual(0, output.returncode)
            self.assertFalse(output.stderr)
            dest_file = temp / "example_pb2.py"
            self.assertTrue(dest_file.is_file())
