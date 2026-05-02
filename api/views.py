from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils import timezone           # <-- FIXED: Added Timezone
from datetime import timedelta              # <-- FIXED: Added Timedelta
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from .models import Item, RentalTransaction # Combined to keep it clean
from .serializers import ItemSerializer

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated]) 
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
        # 1. Check if the Student ID (username) is already taken
        if User.objects.filter(username=data['username']).exists():
            return Response({"error": "That Student ID is already registered!"}, status=status.HTTP_400_BAD_REQUEST)

        # 2. Create the user and catch the email
        user = User.objects.create_user(
            username=data['username'],
            email=data.get('email', ''), 
            password=data['password']
        )
        
        # 3. FIX: Split the full name into First and Last!
        raw_full_name = data.get('full_name', '').strip()
        
        # If there is a space, split it into two pieces
        if ' ' in raw_full_name:
            first, last = raw_full_name.split(' ', 1)
            user.first_name = first
            user.last_name = last
        else:
            # If they only typed one word, just put it in first name
            user.first_name = raw_full_name 
            
        user.save()

        return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    print("\n--- NEW LOGIN ATTEMPT ---")
    print(f"Username typed: '{username}'")
    print(f"Password typed: '{password}'")
    print("-------------------------\n")

    user = authenticate(username=username, password=password)
    
    if user is not None:
        token, created = Token.objects.get_or_create(user=user)
        print("Success! Token generated.")
        return Response({
            "token": token.key, 
            "message": "Login successful"
        }, status=status.HTTP_200_OK)
    else:
        print("Failed! Django could not find a match for that exact username/password.")
        return Response({"error": "Invalid credentials."}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    user = request.user 
    
    member_since = user.date_joined.strftime("%B %Y")
    
    listings_count = 0 
    rentals_count = 0
    reviews_count = 0
    trust_score = 100 

    return Response({
        "username": user.username,
        "email": user.email,
        "full_name": user.get_full_name().strip() or user.username, 
        "member_since": member_since,
        "trust_score": trust_score,
        "rentals_count": rentals_count,
        "listings_count": listings_count,
        "reviews_count": reviews_count
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def checkout(request):
    user = request.user
    item_ids = request.data.get('item_ids', []) 
    
    if not item_ids:
        return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

    return_date = timezone.now() + timedelta(days=3)
    
    successful_rentals = 0

    for item_id in item_ids:
        try:
            item = Item.objects.get(id=item_id)
            
            if item.status == 'Occupied':
                continue 
            
            RentalTransaction.objects.create(
                user=user,
                item=item,
                return_date=return_date,
                total_price=item.price 
            )
            
            item.status = 'Occupied'
            item.save()
            successful_rentals += 1
            
        except Item.DoesNotExist:
            continue
            
    if successful_rentals > 0:
        return Response({"message": f"Successfully processed {successful_rentals} items!"}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Items are no longer available."}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_rentals(request):
    # Find all transactions belonging to the user who made the request
    rentals = RentalTransaction.objects.filter(user=request.user).order_by('-rental_date')
    
    # Manually serialize the data so we can format it perfectly for the Dashboard
    data = []
    for r in rentals:
        data.append({
            "id": r.id,
            "item_title": r.item.title,
            "locker_label": r.item.locker_label,
            "rental_date": r.rental_date.strftime("%b %d, %I:%M %p"),
            "return_date": r.return_date.strftime("%b %d, %Y"),
            "status": "Active" if r.return_date > timezone.now() else "Overdue"
        })
        
    return Response(data, status=status.HTTP_200_OK)