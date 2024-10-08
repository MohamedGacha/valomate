from django.urls import path
from .views import PlatformUpdateView, SelectAgentsView, SetValorantProfileView, UpdateUserAgentPlatformView, UpdateUserAgentRegionView, UserAgentListUpdateView, UserAgentRankSelectView, UserRankUpdateView, ValorantMeView

urlpatterns = [
    path('user/agents/select/', SelectAgentsView.as_view(), name='select-agents'),
    path('user/agent/update/', UserAgentListUpdateView.as_view(), name='update-user-agents'),
    path('user/agent/bulk-update/', UserAgentListUpdateView.as_view(), name='user_agent_list_update'),
    path('user/platform/update/', PlatformUpdateView.as_view(), name='update-platform'),
    path('user/rank/update/', UserRankUpdateView.as_view(), name='user-rank-update'),
    path('user/rank/select/', UserAgentRankSelectView.as_view(), name='user-agent-rank-select'),
    path('user/region/update/', UpdateUserAgentRegionView.as_view(), name='update_user_agent_region'),
    path('valorant-profile/', SetValorantProfileView.as_view(), name='set_valorant_profile'),
    path('valorant/me/', ValorantMeView.as_view(), name='valorant_me'),
]

