from rest_framework import serializers
from .models import Rank, UserAgent, Agent, Platform

class UserAgentSerializer(serializers.ModelSerializer):
    agent = serializers.CharField()
    platform = serializers.CharField()

    class Meta:
        model = UserAgent
        fields = ['id', 'riot_id', 'region', 'agent', 'platform', 'play_style', 'rank']

    def to_internal_value(self, data):
        # Look up agent by name
        agent_name = data.get('agent')
        platform_name = data.get('platform')

        if not agent_name:
            raise serializers.ValidationError({'agent': 'Agent name is required.'})

        if not platform_name:
            raise serializers.ValidationError({'platform': 'Platform name is required.'})

        try:
            agent = Agent.objects.get(name=agent_name)
        except Agent.DoesNotExist:
            raise serializers.ValidationError({'agent': 'Agent does not exist'})

        try:
            platform = Platform.objects.get(platform=platform_name.upper())
        except Platform.DoesNotExist:
            raise serializers.ValidationError({'platform': 'Platform does not exist'})

        data['agent'] = agent.id  # Replace agent name with ID
        data['platform'] = platform.id  # Replace platform name with ID

        return super().to_internal_value(data)
        
    
class UserAgentPlatformUpdateSerializer(serializers.ModelSerializer):
    platform = serializers.CharField()

    class Meta:
        model = UserAgent
        fields = ['platform']

    def validate_platform(self, value):
        try:
            platform = Platform.objects.get(platform=value.upper())
        except Platform.DoesNotExist:
            raise serializers.ValidationError('Platform does not exist')
        return platform.id  # Return platform ID after validation

    def update(self, instance, validated_data):
        platform_id = validated_data.get('platform')
        instance.platform_id = platform_id
        instance.save()
        return instance

class UserAgentListUpdateSerializer(serializers.ModelSerializer):
    agent = serializers.CharField()  # Accept agent name instead of ID
    play_style = serializers.CharField(max_length=500)

    class Meta:
        model = UserAgent
        fields = ['agent', 'play_style']

    def to_internal_value(self, data):
        agent_name = data.get('agent')

        # Validate agent existence
        try:
            agent = Agent.objects.get(name=agent_name)
        except Agent.DoesNotExist:
            raise serializers.ValidationError({'agent': 'Agent does not exist'})

        # Replace agent name with its corresponding ID
        data['agent'] = agent.id

        return super().to_internal_value(data)

class UserAgentBulkUpdateSerializer(serializers.Serializer):
    agents = UserAgentListUpdateSerializer(many=True)

    def update(self, instance, validated_data):
        user = instance
        agents_data = validated_data['agents']

        # Clear existing user-agent records to update the list completely
        UserAgent.objects.filter(user=user).delete()

        # Create new UserAgent records based on the provided data
        for agent_data in agents_data:
            UserAgent.objects.create(
                user=user,
                agent_id=agent_data['agent'],
                play_style=agent_data['play_style']
            )
        return user
    
class RankSerializer(serializers.ModelSerializer):
    rank = serializers.CharField()

    class Meta:
        model = Rank
        fields = ['rank']

    def validate_rank(self, value):
        # Check if the rank name exists in the database
        if not Rank.objects.filter(rank=value).exists():
            raise serializers.ValidationError("Rank does not exist.")
        return value

    def update(self, instance, validated_data):
        # Update the rank instance
        instance.rank = Rank.objects.get(rank=validated_data['rank'])
        instance.save()
        return instance