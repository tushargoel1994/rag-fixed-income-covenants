import json
import boto3

class BedrockLLM:
    """AWS Bedrock integration for LLM responses"""
    
    def __init__(self, model_id: str = 'amazon.nova-2-lite-v1:0', region: str = 'us-east-2'):
        self.model_id = model_id
        self.bedrock = boto3.client('bedrock-runtime', region_name=region)
    
    def generate(self, prompt: str, max_tokens: int = 2000, temperature: float = 0.7) -> str:
        """Generate response using Bedrock"""
        
        body = json.dumps({
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        })
        
        try:
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                body=body
            )
            
            response_body = json.loads(response['body'].read())
            return response_body['output']['message']['content'][0]['text']
        
        except Exception as e:
            return f"Error generating response: {str(e)}"