# coding=utf8
import pytest
from mktxp.rsc.parser import RSCParser
from mktxp.rsc.middleware.scripts import ScriptExtractor
from mktxp.rsc.engine import RSCEngine


MOCK_SCRIPT_EXPORT = """
/system script
add name=ShortScript owner=admin source="/tool fetch url=https://example.com/test;"
add name="Medium Script" owner=admin source="/system/backup/cloud print;\\ndelay 2s;\\n/system/backup/cloud remove-file 0;\\n"
add name=ComplexScript owner=admin source="#\\_Script: ComplexScript.rsc\\r\\n:local testVar \\"my_val\\";\\r\\n:log info \\$testVar;\\n"
"""


def test_script_extraction_and_unescaping():
    parser = RSCParser()
    config = parser.parse(MOCK_SCRIPT_EXPORT)

    extractor = ScriptExtractor(enabled=True)
    processed_config = extractor.process(config)

    assert len(processed_config.extracted_scripts) == 3
    script_names = [s.name for s in processed_config.extracted_scripts]
    assert "ShortScript" in script_names
    assert "Medium Script" in script_names
    assert "ComplexScript" in script_names

    # Check unescaping of CRLF, variable escapes, and quotes
    complex_script = next(s for s in processed_config.extracted_scripts if s.name == "ComplexScript")
    assert '# Script: ComplexScript.rsc' in complex_script.source_code
    assert ':local testVar "my_val";' in complex_script.source_code
    assert ':log info $testVar;' in complex_script.source_code
    assert '\r' not in complex_script.source_code

    # Check parent section replaced with pointer notes
    cmds = processed_config.sections[0].commands
    assert len(cmds) == 3
    assert cmds[0].note_comment == "# Note: ShortScript script source is exported to ShortScript.rsc in this directory"
    assert cmds[1].note_comment == "# Note: Medium Script script source is exported to Medium Script.rsc in this directory"
    assert cmds[2].note_comment == "# Note: ComplexScript script source is exported to ComplexScript.rsc in this directory"


def test_script_extraction_disabled_leaves_inline():
    parser = RSCParser()
    config = parser.parse(MOCK_SCRIPT_EXPORT)

    extractor = ScriptExtractor(enabled=False)
    processed_config = extractor.process(config)

    assert len(processed_config.extracted_scripts) == 0

    cmds = processed_config.sections[0].commands
    assert len(cmds) == 3
    assert cmds[0].command == "add"
    assert "source" in cmds[0].params
    assert cmds[1].command == "add"
    assert "source" in cmds[1].params
    assert cmds[2].command == "add"
    assert "source" in cmds[2].params


def test_rsc_engine_split_script_modes(tmp_path):
    engine = RSCEngine()

    # 1. Default mode (extract_scripts=False): scripts stay inline in 03-system.rsc
    out_default = engine.split(
        raw_text=MOCK_SCRIPT_EXPORT,
        output_dir=str(tmp_path / "default"),
        extract_scripts=False
    )
    assert "03-system.rsc" in out_default
    assert "ShortScript.rsc" not in out_default
    assert "Medium Script.rsc" not in out_default
    assert "ComplexScript.rsc" not in out_default
    assert 'add name=ShortScript' in out_default["03-system.rsc"]
    assert 'add name="Medium Script"' in out_default["03-system.rsc"]
    assert 'add name=ComplexScript' in out_default["03-system.rsc"]

    # 2. Extracted mode (extract_scripts=True): scripts extracted into separate files
    out_extracted = engine.split(
        raw_text=MOCK_SCRIPT_EXPORT,
        output_dir=str(tmp_path / "extracted"),
        extract_scripts=True
    )
    assert "03-system.rsc" in out_extracted
    assert "ShortScript.rsc" in out_extracted
    assert "Medium Script.rsc" in out_extracted
    assert "ComplexScript.rsc" in out_extracted
    assert "# Note: ShortScript script source is exported to ShortScript.rsc in this directory" in out_extracted["03-system.rsc"]
    assert "# Note: Medium Script script source is exported to Medium Script.rsc in this directory" in out_extracted["03-system.rsc"]
    assert "# Note: ComplexScript script source is exported to ComplexScript.rsc in this directory" in out_extracted["03-system.rsc"]
