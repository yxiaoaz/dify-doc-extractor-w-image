import base64
from collections.abc import Generator
from typing import Any
import json


import fitz

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.file.file import File


class Extract(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        
        input_file: File = tool_parameters.get("input_file")
        if not input_file or not isinstance(input_file, File):
            raise ValueError("Not a valid file for input input_file")
        
        input_file_bytes = input_file.blob
        doc = fitz.open(stream = input_file_bytes)
        
        for page in doc:
            blocks = json.loads(page.get_text("json"))['blocks']

            for block in blocks:
                block_type = block['type']

                # text
                if block_type == 0:
                    for line in block['lines']:
                        text = line['spans'][0]['text']
                        yield self.create_text_message(text)
                # image
                elif block_type == 1:
                    base64_image_str = block['image']
                    result_file_bytes = base64.decodebytes(base64_image_str.encode())
                    yield self.create_blob_message(
                        blob=result_file_bytes,
                        meta={
                            "mime_type": f"image/{block['ext']}",
                            "filename": "img",
                        },
                    )
