from django.urls import path
from .views import (
    MyFriendsView, SendFriendRequestView, RespondFriendRequestView,
    FriendFeedView, MyChallengesView, SendChallengeView
)

urlpatterns = [
    path('friends/',                     MyFriendsView.as_view(),            name='social-friends-list'),
    path('friends/request/',             SendFriendRequestView.as_view(),    name='social-friend-request'),
    path('friends/<int:pk>/respond/',    RespondFriendRequestView.as_view(), name='social-friend-respond'),
    path('feed/',                        FriendFeedView.as_view(),           name='social-feed'),
    path('challenges/',                  MyChallengesView.as_view(),         name='social-challenges'),
    path('challenges/send/',             SendChallengeView.as_view(),        name='social-challenge-send'),
]
