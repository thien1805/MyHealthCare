# backend/services/ai_service.py
from datetime import datetime
from openai import OpenAI
import os
import json
from django.core.cache import cache
from apps.appointments.models import Department

class OpenRouterService:
    """
    AI Service using OpenRouter API for:
    1. Medical department suggestion based on symptoms
    2. Health Q&A chatbot
    """
    
    def __init__(self):
        self.api_key = os.environ.get('OPENROUTER_API_KEY', '')
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = "tngtech/deepseek-r1t2-chimera:free"
        self.site_url = "https://myhealthcare-api-h3amhrevg2feeab9.southeastasia-01.azurewebsites.net"
        
        # Debug log
        print(f"[AI Service] API Key configured: {'Yes' if self.api_key else 'No - OPENROUTER_API_KEY not found in environment'}")
        
        # Initialize OpenAI client with OpenRouter base URL
        self.client = None
        if self.api_key:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                default_headers={
                    "HTTP-Referer": self.site_url,
                    "X-Title": "MyHealthCare AI Service",
                }
            )
        else:
            print("[AI Service] WARNING: OpenRouter API key not configured. AI features will not work.")
    
    def _get_available_departments(self):
        """
        Get list of active departments from the database
        Cache for 1 hourre to reduce DB queries
        """
        cache_key = "ai_departments_list"
        departments = cache.get(cache_key)
        
        if departments is None:
            departments = Department.objects.filter(is_active=True).values_list('name', flat=True).order_by('name')
            departments = list(departments)
            cache.set(cache_key, departments, 3600)  # Cache for 1 hour (3600 seconds)
            
        return departments
    
    def _format_departments_list(self):
        """
        Format the list of departments for AI prompt
        """
        departments = self._get_available_departments()
        if not departments:
            return "No department available in the system."
        return "\n".join([f"- {dept}" for dept in departments])
    
    def chat_completion(self, messages, model=None):
        """
        General chat completion via OpenRouter API
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name (default: Claude 3.5 Sonnet)
        
        Returns:
            str: Response content or None if error
        """
        if not self.client:
            return {"error": "API key not configured."}
        
        model = model or self.model
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenRouter API Error: {str(e)}")
            return None
    
    def _calculate_age(self, date_of_birth):
        if not date_of_birth:
            return None
    
        today = datetime.now().date()
        age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
        return age if age >= 0 else None
    
    def suggest_department(self, symptoms, patient_user=None):
        """
        Suggest medical department based on symptoms
        Args:
            symptoms_description: Description of symptoms provided by user
            patient_info: Optional dict with patient details
        Returns:
            dict: Parsed JSON with suggested department, reason.
            Returns error message if parsing fails.
        Example response:
        {
            "department": "Cardiology",
            "reason": "The symptoms described indicate potential heart-related issues...",
            "urgency": "high"
        }
        """ 
        
        departments_list = self._format_departments_list()
        
        system_prompt = f"""You are a medical assistant AI for a healthcare appointment system.
                Your task is to suggest the most appropriate medical department based on the patient's symptoms.
                The available departments are:
                {departments_list}
        **Requirements:**
            1. Suggest only clinics in the above list
            2. Return JSON response with the following structure:
                {
                    "primary_department": "primary clinic name",
                    "reason": "brief explanation in Vietnamese",
                    "urgency": "low|medium|high",
                }
            3. Be careful: if symptoms are unclear or vague, suggest "Internal Medicine Department" as the primary clinic
            4. Return JSON only, no other text
            5. Reply in language with which the patient interacted (Vietnamese or English)
            """
        
        user_message = f"The symptoms of patient: {symptoms}"
        if patient_user and hasattr(patient_user, 'patient_profile'):
            patient_profile = patient_user.patient_profile
            if patient_profile.date_of_birth:
                age = self._calculate_age(patient_profile.date_of_birth)
                if age:
                    user_message += f"\nAge: {age} years old"
            
            if patient_profile.gender:
                gender_display = dict(patient_profile.GENDER_CHOICES).get(patient_profile.gender, patient_profile.gender)
                user_message += f"\nGender: {gender_display}"
        # Construct messages for chat completion 
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        response_text = self.chat_completion(messages)
        if not response_text:
            return {"error": "Failed to get response from AI service."}
        
        try:
            #Extract Json from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                response_json = json.loads(json_str)
                return response_json
            else:
                return {"error": "No JSON object found in AI response.", "raw_response": response_text}
        except json.JSONDecodeError as e:
            return {"error": f"JSON parsing error: {str(e)}", "raw_response": response_text}
         
    def health_chatbot(self, user_message, conversation_history=None):
        """Health Q&A chatbot for general health inquiries
            
            Args:
                user_message: Patient's question or message
                conversation_history: Optional list of previous messages for context )dicts with 'role' and 'content')
                
            Returns:
                str: Chatbot response or None if error
            
            Example:
                - User: "Cảm cúm có nguy hiểm không?"
                - Bot: "Cảm cúm thường không nguy hiểm nhưng cần theo dõi... Nếu triệu chứng nặng, vui lòng đặt lịch khám với bác sĩ"
        """
        system_prompt = """Bạn là một trợ lý y tế hữu ích cho ứng dụng MyHealthCare.

                    **Trách nhiệm của bạn:**
                        - Cung cấp thông tin y tế chung và lời khuyên
                        - Giúp bệnh nhân hiểu các triệu chứng
                        - Hướng dẫn bệnh nhân khi nào cần khám bác sĩ
                        - Trả lời các câu hỏi về thủ tục khám bệnh

                    **Quy tắc quan trọng:**
                        - LUÔN làm rõ rằng bạn không thay thế chẩn đoán y tế chuyên nghiệp
                        - Khuyến khích bệnh nhân đặt lịch khám nếu những lo ngại là nghiêm trọng
                        - Thân thiện, chuyên nghiệp và giàu cảm thương
                        - Trả lời bằng tiếng Việt hoặc tiếng Anh tùy theo ngôn ngữ của bệnh nhân
                    - Giới hạn câu trả lời trong 200-300 từ"""
        messages = [{"role": "system", "content": system_prompt}]
            
            #Add conversation history if available 
        if conversation_history and isinstance(conversation_history, list):
            messages.extend(conversation_history)
            
        messages.append({"role": "user", "content": user_message})
        
            
        response = self.chat_completion(messages)
        return response if response else "Sorry, I couldn't process your request at the moment. Please try again later."
    
    
#Singleton instance
ai_service = OpenRouterService()
            
        
        