from flask import Blueprint, request, jsonify
from services.chatbot_service import ChatbotService
import requests

api_bp = Blueprint('api', __name__)
chatbot = ChatbotService()

@api_bp.route('/api/chatbot', methods=['POST'])
def chatbot_endpoint():
    """Chatbot API endpoint"""
    data = request.json
    message = data.get('message', '')
    
    if not message:
        return jsonify({'error': 'Message is required'}), 400
    
    response = chatbot.get_response(message)
    return jsonify(response)

@api_bp.route('/api/youtube/search', methods=['GET'])
def youtube_search():
    """YouTube search API endpoint"""
    query = request.args.get('query', '')
    
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    # Add disability context to search
    search_query = f"{query} disability India support"
    
    # Mock YouTube API response (replace with actual API call)
    mock_videos = [
        {
            'title': 'Disability Rights in India - Complete Guide',
            'videoId': 'dQw4w9WgXcQ',
            'channel': 'Rights Channel'
        },
        {
            'title': 'Understanding PwD Act 2016',
            'videoId': 'dQw4w9WgXcQ',
            'channel': 'Legal Awareness'
        }
    ]
    
    return jsonify({'videos': mock_videos, 'query': search_query})

@api_bp.route('/api/analyze/certificate', methods=['POST'])
def analyze_certificate():
    """Analyze disability certificate (mock)"""
    # In production, integrate with OCR/AI service
    return jsonify({
        'success': True,
        'analysis': {
            'disability_type': 'Visual Impairment',
            'severity': 'Moderate (40-70%)',
            'recommendations': 'Screen reader software, Braille training'
        }
    })