"""
Pipeline Service for Automatic Operation Chaining

This service determines what operations are needed based on input type and desired output,
then chains them automatically. Examples:

- ASR: Hindi audio → Hindi text (same language)
- ASR+MT: Hindi audio → English text (audio in Hindi, want English text)  
- MT: Hindi text → English text (different languages)
- MT+TTS: Hindi text → English audio (text in Hindi, want English audio)
- ASR+MT+TTS: Hindi audio → English audio (audio in Hindi, want English audio)
- TTS: Hindi text → Hindi audio (same language)
- OCR: Hindi image → Hindi text (same language)
- OCR+MT: Hindi image → English text (image in Hindi, want English text)
- OCR+MT+TTS: Hindi image → English audio (image in Hindi, want English audio)
"""

from typing import Optional, Union, Tuple, Dict, Any
from fastapi import UploadFile
from enum import Enum

from .bhashini import asr_transcribe, mt_translate, tts_synthesize, ocr_extract
from ..utils.languages import validate_language, LANGUAGE_NAMES

class InputType(str, Enum):
    TEXT = "text"
    AUDIO = "audio" 
    IMAGE = "image"

class OutputType(str, Enum):
    TEXT = "text"
    AUDIO = "audio"

class PipelineResult:
    def __init__(self):
        self.final_output: Any = None
        self.intermediate_results: Dict[str, Any] = {}
        self.operations_performed: list[str] = []
        self.source_language: str = ""
        self.target_language: str = ""
        self.input_type: str = ""
        self.output_type: str = ""

def determine_required_operations(
    input_type: InputType, 
    output_type: OutputType, 
    source_lang: str, 
    target_lang: str
) -> list[str]:
    """
    Determine what operations are needed based on input/output types and languages.
    
    Returns list of operations in order: ['asr', 'mt', 'tts']
    """
    operations = []
    
    # Step 1: Convert input to text if needed
    if input_type == InputType.AUDIO:
        operations.append('asr')
    elif input_type == InputType.IMAGE:
        operations.append('ocr')
    # If input_type is TEXT, no conversion needed
    
    # Step 2: Translate if languages are different
    if source_lang != target_lang:
        operations.append('mt')
    
    # Step 3: Convert to audio if needed
    if output_type == OutputType.AUDIO:
        operations.append('tts')
    
    return operations

async def execute_pipeline(
    input_data: Union[str, UploadFile],
    input_type: InputType,
    output_type: OutputType,
    source_language: str,
    target_language: str,
    gender: Optional[str] = "female"
) -> PipelineResult:
    """
    Execute the complete pipeline based on input/output requirements.
    
    Args:
        input_data: Text string, audio file, or image file
        input_type: Type of input (text/audio/image)
        output_type: Desired output type (text/audio)  
        source_language: Language of the input
        target_language: Desired output language
        gender: Voice gender for TTS (if needed)
    
    Returns:
        PipelineResult with final output and metadata
    """
    # Validate languages
    source_lang = validate_language(source_language)
    target_lang = validate_language(target_language)
    
    # Initialize result
    result = PipelineResult()
    result.source_language = source_lang
    result.target_language = target_lang
    result.input_type = input_type.value
    result.output_type = output_type.value
    
    # Determine required operations
    operations = determine_required_operations(input_type, output_type, source_lang, target_lang)
    result.operations_performed = operations
    
    # Start with input data
    current_data = input_data
    current_lang = source_lang
    
    # Execute each operation in sequence
    for operation in operations:
        if operation == 'asr':
            # Audio to text in source language
            current_data = await asr_transcribe(current_data, language=current_lang)
            result.intermediate_results['asr_text'] = current_data
            
        elif operation == 'ocr':
            # Image to text in source language
            current_data = await ocr_extract(current_data, language=current_lang) 
            result.intermediate_results['ocr_text'] = current_data
            
        elif operation == 'mt':
            # Translate from source to target language
            current_data = await mt_translate(current_data, source_lang, target_lang)
            result.intermediate_results['translated_text'] = current_data
            current_lang = target_lang  # Language has changed
            
        elif operation == 'tts':
            # Text to speech in current language (should be target language by now)
            current_data = await tts_synthesize(current_data, gender, language=current_lang)
            result.intermediate_results['tts_audio_url'] = current_data
    
    # Set final output
    result.final_output = current_data
    
    return result

# Helper functions for common pipelines

async def text_to_text_pipeline(
    text: str,
    source_language: str, 
    target_language: str
) -> PipelineResult:
    """Text → Text pipeline (MT only if different languages)"""
    return await execute_pipeline(
        input_data=text,
        input_type=InputType.TEXT,
        output_type=OutputType.TEXT,
        source_language=source_language,
        target_language=target_language
    )

async def text_to_audio_pipeline(
    text: str,
    source_language: str,
    target_language: str, 
    gender: str = "female"
) -> PipelineResult:
    """Text → Audio pipeline (MT + TTS, or just TTS if same language)"""
    return await execute_pipeline(
        input_data=text,
        input_type=InputType.TEXT,
        output_type=OutputType.AUDIO,
        source_language=source_language,
        target_language=target_language,
        gender=gender
    )

async def audio_to_text_pipeline(
    audio_file: UploadFile,
    source_language: str,
    target_language: str
) -> PipelineResult:
    """Audio → Text pipeline (ASR + MT, or just ASR if same language)"""
    return await execute_pipeline(
        input_data=audio_file,
        input_type=InputType.AUDIO,
        output_type=OutputType.TEXT,
        source_language=source_language,
        target_language=target_language
    )

async def audio_to_audio_pipeline(
    audio_file: UploadFile,
    source_language: str,
    target_language: str,
    gender: str = "female"
) -> PipelineResult:
    """Audio → Audio pipeline (ASR + MT + TTS, or ASR + TTS if same language)"""
    return await execute_pipeline(
        input_data=audio_file,
        input_type=InputType.AUDIO,
        output_type=OutputType.AUDIO,
        source_language=source_language,
        target_language=target_language,
        gender=gender
    )

async def image_to_text_pipeline(
    image_file: UploadFile,
    source_language: str,
    target_language: str
) -> PipelineResult:
    """Image → Text pipeline (OCR + MT, or just OCR if same language)"""
    return await execute_pipeline(
        input_data=image_file,
        input_type=InputType.IMAGE,
        output_type=OutputType.TEXT,
        source_language=source_language,
        target_language=target_language
    )

async def image_to_audio_pipeline(
    image_file: UploadFile,
    source_language: str,
    target_language: str,
    gender: str = "female"
) -> PipelineResult:
    """Image → Audio pipeline (OCR + MT + TTS, or OCR + TTS if same language)"""
    return await execute_pipeline(
        input_data=image_file,
        input_type=InputType.IMAGE,
        output_type=OutputType.AUDIO,
        source_language=source_language,
        target_language=target_language,
        gender=gender
    )