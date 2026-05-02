from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Item
from .serializers import ItemSerializer
from rest_framework.authtoken.models import Token

@api_view(['GET', 'POST'])
def item_list(request):
    if request.method == 'GET':
        items = Item.objects.all()
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = ItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def register_user(request):
    data = request.data
    try:
        user = User.objects.create_user(
            username=data['username'],
            password=data['password']
        )
        return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    # Check if the user exists and the password matches
    user = authenticate(username=username, password=password)
    
    if user is not None:
        # Generate or retrieve the token for this user
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            "token": token.key, 
            "message": "Login successful"
        }, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Invalid credentials."}, status=status.HTTP_400_BAD_REQUEST)