from django.core.management.base import BaseCommand
from valorantProfile.models import Agent, Platform, Rank, Region

class Command(BaseCommand):
    help = "Populates the database with initial data for agents, platforms, ranks, and regions."

    def handle(self, *args, **options):
        # Populate Agents
        agents_data = {
            'Controller': Agent.CONTROLLERS,
            'Sentinel': Agent.SENTINELS,
            'Duelist': Agent.DUALISTS,
            'Initiator': Agent.INITIATORS,
        }
        
        for category, agents in agents_data.items():
            for agent_name in agents:
                agent, created = Agent.objects.get_or_create(name=agent_name)
                agent.category = category  # Set the category based on the group
                agent.save()
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Agent {agent_name} ({category}) added.'))
                else:
                    self.stdout.write(self.style.WARNING(f'Agent {agent_name} ({category}) already exists.'))

        # Populate Platforms
        platforms = [choice[0] for choice in Platform.PLATFORM_CHOICES]
        for platform_name in platforms:
            platform, created = Platform.objects.get_or_create(platform=platform_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Platform {platform_name} added.'))
            else:
                self.stdout.write(self.style.WARNING(f'Platform {platform_name} already exists.'))

        # Populate Ranks
        ranks = [choice[0] for choice in Rank.RANK_CHOICES]
        for rank_name in ranks:
            rank, created = Rank.objects.get_or_create(rank=rank_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Rank {rank_name} added.'))
            else:
                self.stdout.write(self.style.WARNING(f'Rank {rank_name} already exists.'))

        # Populate Regions
        regions = [choice for choice in Region.REGION_CHOICES]
        for code, name in regions:
            region, created = Region.objects.get_or_create(code=code)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Region {name} ({code}) added.'))
            else:
                self.stdout.write(self.style.WARNING(f'Region {name} ({code}) already exists.'))

        self.stdout.write(self.style.SUCCESS('Database populated successfully!'))