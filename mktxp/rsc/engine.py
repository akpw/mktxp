# coding=utf8
## Copyright (c) 2026 Arseniy Kuznetsov
##
## This program is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License
## as published by the Free Software Foundation; either version 2
## of the License, or (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

import os
from typing import Dict, List, Optional, Tuple, Any
from .ast import RSCConfig, ScriptNode, SectionNode
from .parser import RSCParser
from .formatter import RSCFormatter
from .middleware.pipeline import MiddlewarePipeline
from .middleware.sorter import DeterminismSorter
from .middleware.scripts import ScriptExtractor
from .middleware.sanitizer import Sanitizer
from .handlers.chain import HandlerChain, DEFAULT_HANDLER_ORDER, DEFAULT_HANDLER_CONFIG


class RSCEngine:
    """
    High-level orchestrator for RouterOS GitOps formatting and splitting operations.
    """

    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        self.config_dict = config_dict or {}
        self.handler_order = self._get_handler_order()
        self.handler_config = self._get_handler_config()

    def _get_handler_order(self) -> List[str]:
        if 'handler_order' in self.config_dict:
            val = self.config_dict['handler_order']
            if isinstance(val, str):
                return [x.strip() for x in val.split(',') if x.strip()]
            elif isinstance(val, list):
                return val
        return list(DEFAULT_HANDLER_ORDER)

    def _get_handler_config(self) -> Dict[str, List[str]]:
        cfg = dict(DEFAULT_HANDLER_CONFIG)
        for k, v in self.config_dict.items():
            if k.startswith('handler_') and k != 'handler_order':
                if isinstance(v, str):
                    cfg[k] = [p.strip() for p in v.split(',') if p.strip()]
                elif isinstance(v, list):
                    cfg[k] = v
        return cfg

    def parse_and_process(
        self,
        raw_text: str,
        extract_scripts: bool = False,
        strip_dynamic_macs: bool = False
    ) -> RSCConfig:
        parser = RSCParser()
        ast_config = parser.parse(raw_text)

        pipeline = MiddlewarePipeline([
            DeterminismSorter(),
            ScriptExtractor(enabled=extract_scripts),
            Sanitizer(strip_dynamic_macs=strip_dynamic_macs)
        ])

        return pipeline.execute(ast_config)

    def format(
        self,
        raw_text: str,
        wrap_lines: bool = False,
        wrap_col: int = 80,
        extract_scripts: bool = False,
        strip_dynamic_macs: bool = False,
        add_section_headers: bool = True,
        include_header_comments: bool = False
    ) -> Tuple[str, List[ScriptNode]]:
        config = self.parse_and_process(
            raw_text,
            extract_scripts=extract_scripts,
            strip_dynamic_macs=strip_dynamic_macs
        )

        chain = HandlerChain(
            handler_order=self.handler_order,
            handler_config=self.handler_config
        )
        active_handlers = chain.process_sections(config.sections)

        # Assemble all sections ordered by handler chain
        ordered_sections: List[SectionNode] = []
        for handler in active_handlers:
            ordered_sections.extend(handler.claimed_sections)

        ordered_config = RSCConfig(
            sections=ordered_sections,
            header_comments=config.header_comments,
            extracted_scripts=config.extracted_scripts
        )

        formatter = RSCFormatter(
            wrap_lines=wrap_lines,
            wrap_col=wrap_col,
            add_section_headers=add_section_headers
        )
        formatted_str = formatter.format_config(
            ordered_config,
            include_header_comments=include_header_comments
        )

        return formatted_str, config.extracted_scripts

    def split(
        self,
        raw_text: str,
        output_dir: Optional[str] = None,
        numbered: bool = True,
        wrap_lines: bool = False,
        wrap_col: int = 80,
        extract_scripts: bool = False,
        strip_dynamic_macs: bool = False,
        add_section_headers: bool = True
    ) -> Dict[str, str]:
        config = self.parse_and_process(
            raw_text,
            extract_scripts=extract_scripts,
            strip_dynamic_macs=strip_dynamic_macs
        )

        chain = HandlerChain(
            handler_order=self.handler_order,
            handler_config=self.handler_config
        )
        active_handlers = chain.process_sections(config.sections)

        formatter = RSCFormatter(
            wrap_lines=wrap_lines,
            wrap_col=wrap_col,
            add_section_headers=add_section_headers
        )

        emitted_files: Dict[str, str] = {}

        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        for handler in active_handlers:
            filename = handler.get_output_filename(numbered=numbered)
            sub_config = RSCConfig(sections=handler.claimed_sections)
            content = formatter.format_config(sub_config, include_header_comments=False)
            emitted_files[filename] = content

            if output_dir:
                file_path = os.path.join(output_dir, filename)
                with open(file_path, 'w', encoding='utf8') as f:
                    f.write(content)

        # Output extracted sidecar scripts
        for script_node in config.extracted_scripts:
            script_filename = f"{script_node.name}.rsc"
            script_content = script_node.source_code
            emitted_files[script_filename] = script_content

            if output_dir:
                script_path = os.path.join(output_dir, script_filename)
                with open(script_path, 'w', encoding='utf8') as f:
                    f.write(script_content)

        return emitted_files
