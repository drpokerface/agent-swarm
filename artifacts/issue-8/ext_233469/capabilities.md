# Capabilities Probe Findings

- Image Generation: Imagen 3.0 failed - 404 NOT_FOUND. {'error': {'code': 404, 'message': 'models/imagen-3.0-generate-001 is not found for API version v1beta, or is not supported for predict. Call ModelService.ListModels to see the list of available models and their supported methods.', 'status': 'NOT_FOUND'}}
- Image Generation: Imagen 4.0 failed - 404 NOT_FOUND. {'error': {'code': 404, 'message': 'This model models/imagen-4.0-generate-001 is no longer available to new users. Please update your code to use a newer model for the latest features and improvements. We recommend you to use the Interactions API (https://ai.google.dev/gemini-api/docs/migrate-to-interactions).', 'status': 'NOT_FOUND'}}
- TTS Audio: edge-tts is available and generates clear mp3 speech successfully.
- Video Assembly: ffmpeg is installed and available for assembling slices.


## API Limits
Gemini API: Standard quota limits apply. Edge-TTS: Free, rate limited by MS.
