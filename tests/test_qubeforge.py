import contextlib
import io
import json
import pathlib
import sys
import tempfile
import tomllib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import qubeforge


class QubeForgeTests(unittest.TestCase):
    def test_load_profile_and_render_plan(self):
        profile = qubeforge.load_profile("debian-vault")
        plan = qubeforge.render_plan(profile)

        self.assertEqual(profile.template_name, "debian-12-vault-minimal-audit")
        self.assertEqual(plan["schema"], "qubeforge.plan.v1")
        self.assertEqual(plan["profile"], "debian-vault")
        self.assertEqual(plan["name"]["omitted_parts"], ["hardened"])
        self.assertIn("auditd", plan["payload"]["packages"])
        self.assertIn("QUBEFORGE_PACKAGES", profile.make_env)

    def test_plan_is_json_serializable(self):
        profile = qubeforge.load_profile("fedora-workstation")
        encoded = json.dumps(qubeforge.render_plan(profile))
        self.assertIn("fedora-40", encoded)

    def test_missing_profile_is_user_error(self):
        with self.assertRaises(qubeforge.QubeForgeError):
            qubeforge.load_profile("missing")

    def test_schema_file_is_not_listed_as_profile(self):
        self.assertNotIn("schema", qubeforge.list_profiles())

    def test_template_name_respects_qubes_limit(self):
        profile = qubeforge.Profile(
            name="long",
            dist="debian-12",
            flavor="workstation",
            options=("minimal", "audit", "hardened", "extras"),
            packages=(),
            services=(),
            repos=(),
            notes="",
        )
        self.assertLessEqual(len(profile.template_name), qubeforge.MAX_TEMPLATE_NAME_LENGTH)
        self.assertIn("hardened", profile.name_parts[1])

    def test_validate_command_accepts_all_profiles(self):
        parser = qubeforge.build_parser()
        args = parser.parse_args(["validate"])
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(args.func(args), 0)

    def test_cli_version_is_defined(self):
        self.assertRegex(qubeforge.VERSION, r"^\d+\.\d+\.\d+$")

    def test_cli_version_matches_project_metadata(self):
        with (ROOT / "pyproject.toml").open("rb") as handle:
            metadata = tomllib.load(handle)
        self.assertEqual(qubeforge.VERSION, metadata["project"]["version"])

    def test_format_env_quotes_values_with_spaces(self):
        formatted = qubeforge.format_env({"QUBEFORGE_PACKAGES": "a b"})
        self.assertEqual(formatted, "QUBEFORGE_PACKAGES='a b'")

    def test_write_plan_supports_custom_output_path(self):
        profile = qubeforge.load_profile("debian-vault")
        plan = qubeforge.render_plan(profile)

        with tempfile.TemporaryDirectory() as tmp:
            output = pathlib.Path(tmp) / "plan.json"
            written = qubeforge.write_plan(plan, output)

            self.assertEqual(written, output)
            self.assertTrue(output.exists())
            self.assertEqual(json.loads(output.read_text())["profile"], "debian-vault")

    def test_example_manifest_matches_current_plan_shape(self):
        profile = qubeforge.load_profile("debian-vault")
        plan = qubeforge.render_plan(profile)
        example = json.loads(
            (ROOT / "examples" / "debian-vault.plan.example.json").read_text()
        )
        plan["created_at"] = example["created_at"]
        self.assertEqual(plan, example)

    def test_doctor_can_skip_tool_checks_for_ci(self):
        profile = qubeforge.load_profile("debian-vault")
        report = qubeforge.check_build_environment(profile, skip_tools=True)
        self.assertIsInstance(report.errors, tuple)
        self.assertIn("template name omitted parts", report.warnings[0])


if __name__ == "__main__":
    unittest.main()
