from rest_framework import serializers
from pdfadmin.models import Question, QuestionSection

class QuestionSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionSection
        fields = ["id", "title"]
        read_only_fields = [
            "id"
        ]

class ListQuestionSectionSerializer(serializers.ModelSerializer):
    questionCount = serializers.SerializerMethodField()

    class Meta:
        model = QuestionSection
        fields = ["id", "title", "questionCount"]
        read_only_fields = [
            "id"
        ]
        
    def get_questionCount(self, obj):
        count = Question.objects.filter(section = obj.id)
        return len(count)

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            "id", "content", "section", "correctAnswer", "suggestion"
        ]
        read_only_fields = [
            "id"
        ]
        depth = 2
    
    def create(self, validated_data):
        question = Question(
            content = validated_data['content'],
            section = self.context['section'],
            correctAnswer = validated_data['correctAnswer'],
            suggestion = validated_data['suggestion']
        )
        question.save()
        return question
    
    # def update(self, instance, validated_data):


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class QuestionIdListSerializer(serializers.Serializer):
    ids = serializers.ListField()