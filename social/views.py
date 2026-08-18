from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from .models import Friendship, FriendActivity, ChallengeInvite
from .serializers import FriendshipSerializer, FriendActivitySerializer, ChallengeInviteSerializer


class MyFriendsView(generics.ListAPIView):
    """GET /api/social/friends/ — ჩემი მეგობრების სია"""
    serializer_class   = FriendshipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Friendship.objects.filter(
            Q(from_user=user) | Q(to_user=user),
            status='accepted'
        ).select_related('from_user', 'to_user')


class SendFriendRequestView(APIView):
    """POST /api/social/friends/request/ — მეგობრობის მოთხოვნის გაგზავნა"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        to_user_id = request.data.get('to_user_id')
        if not to_user_id:
            return Response({'error': 'to_user_id საჭიროა'}, status=status.HTTP_400_BAD_REQUEST)

        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            to_user = User.objects.get(id=to_user_id)
        except User.DoesNotExist:
            return Response({'error': 'მომხმარებელი ვერ მოიძებნა'}, status=status.HTTP_404_NOT_FOUND)

        if to_user == request.user:
            return Response({'error': 'საკუთარ თავს ვერ დაამეგობრებ'}, status=status.HTTP_400_BAD_REQUEST)

        # ორმხრივი დუბლიკატის შემოწმება (A→B ან B→A)
        existing = Friendship.objects.filter(
            Q(from_user=request.user, to_user=to_user) |
            Q(from_user=to_user, to_user=request.user)
        ).first()
        if existing:
            return Response({'error': 'მეგობრობის მოთხოვნა უკვე არსებობს'}, status=status.HTTP_400_BAD_REQUEST)

        Friendship.objects.create(from_user=request.user, to_user=to_user)

        return Response({'message': f'{to_user.email}-ს მეგობრობის მოთხოვნა გაეგზავნა'})


class RespondFriendRequestView(APIView):
    """POST /api/social/friends/<id>/respond/ — მოთხოვნაზე პასუხი (accept/decline)"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        action = request.data.get('action')  # 'accept' ან 'decline'
        try:
            friendship = Friendship.objects.get(id=pk, to_user=request.user, status='pending')
        except Friendship.DoesNotExist:
            return Response({'error': 'მოთხოვნა ვერ მოიძებნა'}, status=status.HTTP_404_NOT_FOUND)

        if action == 'accept':
            friendship.status = 'accepted'
            friendship.save()
            return Response({'message': 'მეგობრობა დადასტურდა'})
        elif action == 'decline':
            friendship.delete()
            return Response({'message': 'მოთხოვნა უარყოფილია'})
        return Response({'error': 'action: accept ან decline'}, status=status.HTTP_400_BAD_REQUEST)


class FriendFeedView(generics.ListAPIView):
    """GET /api/social/feed/ — მეგობრების სოციალური არხი"""
    serializer_class   = FriendActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # ვიღებთ ყველა მეგობრის ID-ს
        friends_qs = Friendship.objects.filter(
            Q(from_user=user) | Q(to_user=user),
            status='accepted'
        )
        friend_ids = set()
        for f in friends_qs:
            friend_ids.add(f.from_user_id if f.to_user_id == user.id else f.to_user_id)

        return FriendActivity.objects.filter(
            user_id__in=friend_ids
        ).select_related('user', 'poi', 'badge', 'skin')[:50]


class MyChallengesView(generics.ListAPIView):
    """GET /api/social/challenges/ — ჩემი (გამოგზავნილი + მიღებული) გამოწვევები"""
    serializer_class   = ChallengeInviteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        from django.utils import timezone
        # Auto-expire pending challenges past expires_at
        ChallengeInvite.objects.filter(
            status='pending',
            expires_at__isnull=False,
            expires_at__lt=timezone.now()
        ).update(status='expired')

        return ChallengeInvite.objects.filter(
            Q(from_user=user) | Q(to_user=user)
        ).select_related('from_user', 'to_user', 'poi')


class SendChallengeView(APIView):
    """POST /api/social/challenges/send/ — გამოწვევის გაგზავნა"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        to_user_id = request.data.get('to_user_id')
        poi_id     = request.data.get('poi_id')
        message    = request.data.get('message', '')
        raw_bonus  = request.data.get('bonus_xp', 25)

        try:
            bonus_xp = min(max(10, int(raw_bonus)), 100)
        except (ValueError, TypeError):
            bonus_xp = 25

        if not to_user_id or not poi_id:
            return Response({'error': 'to_user_id და poi_id საჭიროა'}, status=status.HTTP_400_BAD_REQUEST)

        from django.contrib.auth import get_user_model
        from maps.models import PointOfInterest
        User = get_user_model()

        try:
            to_user = User.objects.get(id=to_user_id)
            poi     = PointOfInterest.objects.get(id=poi_id)
        except (User.DoesNotExist, PointOfInterest.DoesNotExist):
            return Response({'error': 'მომხმარებელი ან ლოკაცია ვერ მოიძებნა'}, status=status.HTTP_404_NOT_FOUND)

        # H1 FIX: Verify friendship exists between users
        is_friend = Friendship.objects.filter(
            (Q(from_user=request.user, to_user=to_user) | Q(from_user=to_user, to_user=request.user)),
            status='accepted'
        ).exists()
        if not is_friend:
            return Response({'error': 'გამოწვევის გაგზავნა მხოლოდ მეგობრებისთვისაა ნებადართული'}, status=status.HTTP_403_FORBIDDEN)

        challenge = ChallengeInvite.objects.create(
            from_user=request.user,
            to_user=to_user,
            poi=poi,
            message=message,
            bonus_xp=bonus_xp
        )
        serializer = ChallengeInviteSerializer(challenge)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
