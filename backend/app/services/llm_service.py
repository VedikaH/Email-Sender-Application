import requests
import json
from typing import Dict, List
from ..config import settings
import re

async def generate_email_content(
    situation: str,
    keywords: List[str],
    data: Dict[str, str]
) -> Dict[str, str]:
    """
    Generate email content using LLM with CSV data variables
    
    Args:
        situation: str: The email context/purpose
        keywords: List[str]: Key points to include
        data: Dict[str, str]: Dictionary of template variables from CSV row
    Returns:
        Dict[str, str]: Dictionary containing email subject, html_body, and text_body
    """
    # Format the variable placeholders from dictionary
    variable_list = [f"{{{k}}}: {v}" for k, v in data.items()]
    
    prompt_template = f"""
SITUATION:
{situation}

KEY POINTS TO INCLUDE:
{', '.join(keywords)}

AVAILABLE PERSONALIZATION VARIABLES:
{', '.join(variable_list)}
"""

    try:
        # Make the API call
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "Email Sender App"
            },
            json={
                "model": "meta-llama/llama-3.2-3b-instruct:free",
                "messages": [
                    {
                        "role": "system",
                        "content": '''
                        You are a professional email writer. Create emails that are clear, concise, and appropriate for the given situation. 
                        Return your response as a valid JSON object with the following structure:
                        {
                            "subject": "The email subject line",
                            "html_body": "The HTML formatted email body",
                            "text_body": "The plain text email body"
                        }
                        
                        Important:
                        - Use only the variables provided in AVAILABLE PERSONALIZATION VARIABLES
                        - Keep all newlines as literal '\\n' in the text_body
                        - Ensure HTML is properly formatted in html_body
                        - Return only the JSON object, no markdown formatting or code blocks
                        '''
                    },
                    {
                        "role": "user",
                        "content": prompt_template
                    }
                ],
                "temperature": 0.0,
                "max_tokens": 1000
            }
        )

        # Parse the API response
        llm_response = response.json()
        
        # Get the content
        content = llm_response['choices'][0]['message']['content']
        
        # Print raw content for debugging
        print("Raw content received:", content)
        
        # Remove markdown code blocks and clean the content
        content = re.sub(r'```json\s*', '', content) 
        content = re.sub(r'```\s*', '', content)      
        content = content.strip()
        
        print("Content after markdown removal:", content)
        
        try:
            # Parse the JSON content
            email_content = json.loads(content)
            
            # Validate the dictionary has required fields
            required_fields = ['subject', 'html_body', 'text_body']
            for field in required_fields:
                if field not in email_content:
                    raise ValueError(f"Missing required field: {field}")
                if not isinstance(email_content[field], str):
                    raise ValueError(f"Field {field} must be a string")
                if not email_content[field].strip():
                    raise ValueError(f"Field {field} cannot be empty")

            # Format the dictionary values
            email_content = {
                'subject': email_content['subject'].strip(),
                'html_body': email_content['html_body'].strip(),
                'text_body': email_content['text_body'].replace('\\n', '\n').strip()
            }

            print("Successfully parsed email content:", email_content)
            return email_content
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {str(e)}")
            print(f"Content that failed to parse: {content}")
            raise ValueError(f"Failed to parse JSON content: {str(e)}")

    except requests.exceptions.RequestException as e:
        raise ValueError(f"API request failed: {str(e)}")
    except KeyError as e:
        raise ValueError(f"Invalid response structure: {str(e)}")
    except Exception as e:
        print(f"Full error: {str(e)}")
        print(f"Response content: {content if 'content' in locals() else 'No content available'}")
        raise ValueError(f"Error processing response: {str(e)}")
