import unittest
from . import parse_args


class TestArgs(unittest.TestCase):
    def test_giving_args(self):
        args = parse_args(
            [
                "--input",
                "test.csv",
                "--headers",
                "c1",
                "c2",
                "--heat-size",
                "3",
                "--rounds",
                "5",
            ]
        )
        self.assertEqual(args.input, "test.csv")
        self.assertEqual(args.headers, ["c1", "c2"])
        self.assertEqual(args.heat_size, 3)
        self.assertEqual(args.rounds, 5)

    def test_default_args(self):
        args = parse_args([])
        self.assertEqual(args.input, "riders.csv")
        self.assertEqual(args.headers, ["First Name", "Surname"])
        self.assertEqual(args.heat_size, 2)
        self.assertEqual(args.rounds, 4)


if __name__ == "__main__":
    unittest.main()
